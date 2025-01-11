from impl import MockImplementation as Implementation
from logger import Logger
from pipeline import AsyncFunc, Func, Pipeline, Task
from state import State

class UpdatePipeline(Pipeline):

    @classmethod
    def generate(cls):
        return cls()

    # Run
    async def run(self) -> State:
        # Run the pipeline tasks and return the final state
        results = await super().run()
        return results["get_next_state"]

    # Initialize
    def __init__(self):
        super().__init__()

        # Initialize
        logger = Logger()
        impl = Implementation(logger)

        # Extract states
        self.add_task_async(
            "extract_states",
            lambda: AsyncFunc(impl.extract_states)
        )

        # Get previous state
        self.add_task(
            "get_previous_state",
            lambda states: Func(impl.get_previous_state, states),
            dependencies=["extract_states"]
        )

        # Extract users, tracks, sessions
        self.add_task_async(
            "extract_users", 
            lambda state: AsyncFunc(impl.extract_users, state),
            dependencies=["get_previous_state"]
        )
        
        self.add_task_async(
            "extract_tracks", 
            lambda state: AsyncFunc(impl.extract_tracks, state),
            dependencies=["get_previous_state"]
        )

        self.add_task_async(
            "extract_sessions", 
            lambda state: AsyncFunc(impl.extract_sessions, state),
            dependencies=["get_previous_state"]
        )

        # Normalize users and tracks
        self.add_task(
            "normalize_users", 
            lambda users: Func(impl.normalize_users, users), 
            dependencies=["extract_users"]
        )
        self.add_task(
            "normalize_tracks", 
            lambda tracks: Func(impl.normalize_tracks, tracks), 
            dependencies=["extract_tracks"]
        )

        # Load normalized users and tracks
        self.add_task_async(
            "load_nml_users", 
            lambda nml_users: AsyncFunc(impl.load_nml_users, nml_users), 
            dependencies=["normalize_users"]
        )
        self.add_task_async(
            "load_nml_tracks", 
            lambda nml_tracks: AsyncFunc(impl.load_nml_tracks, nml_tracks), 
            dependencies=["normalize_tracks"]
        )

        # Get sessions lookups and pre-normalization tables
        self.add_task(
            "get_lookup_ctx", 
            lambda sessions: Func(impl.get_lookup_ctx, sessions),
            dependencies=["extract_sessions"]
        )

        # Extract normalized users and tracks
        self.add_task_async(
            "extract_nml_users", 
            lambda lookup_ctx, _: AsyncFunc(impl.extract_nml_users, lookup_ctx),
            dependencies=["get_lookup_ctx", "load_nml_users"]
        )
        self.add_task_async(
            "extract_nml_tracks", 
            lambda lookup_ctx, _: AsyncFunc(impl.extract_nml_tracks, lookup_ctx),
            dependencies=["get_lookup_ctx", "load_nml_tracks"]
        )

        # Normalize sessions
        self.add_task(
            "normalize_sessions", 
            lambda lookup_ctx, nml_users, nml_tracks: Func(impl.normalize_sessions,
                lookup_ctx,
                nml_users,
                nml_tracks,
            ), 
            dependencies=["get_lookup_ctx", "extract_nml_users", "extract_nml_tracks"]
        )

        # Load normalized sessions
        self.add_task_async(
            "load_nml_sessions", 
            lambda nml_sessions: AsyncFunc(impl.load_nml_sessions, nml_sessions), 
            dependencies=["normalize_sessions"]
        )

        # Get next state
        self.add_task(
            "get_next_state", 
            lambda state, users, tracks, sessions: Func(impl.get_next_state,
                state,
                users,
                tracks,
                sessions,
            ),
            dependencies=["get_previous_state", "extract_users", "extract_tracks", "extract_sessions"]
        )

        # Load state and logs
        self.add_task_async(
            "load_state", 
            lambda state: AsyncFunc(impl.load_state, state), 
            dependencies=["get_next_state"]
        )
        self.add_task_async(
            "load_logs", 
            lambda _: AsyncFunc(impl.load_logs),
            dependencies=["load_state"]
        )
