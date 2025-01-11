import asyncio

from src.pipeline import Pipeline, Task, AsyncFunc, Func

'''
Félicitations ! Vous voilà maintenant l'heureux détenteur de l'appli MooVitamix-ENL. LA solution clé en main pour la gestion de vos pipelines de données.
Bienvenue au volant de votre nouvelle application. Vous avez maintenant la possibilité d'observer la bonne santé de vos pipelines de données de manière simple et efficace.
'''

# TODO: test that using a Func or AsyncFunc at the wrong time raises an error 
# TODO: test that using add_task_async with a Func raises an error
# TODO: test that using add_task with an AsyncFunc raises an error

def test_pipeline_task_order():
    # test that the tasks are called in the right order

    order = []

    blue = lambda: order.append("blue")
    red = lambda: order.append("red")
    purple = lambda: order.append("purple")
    yellow = lambda: order.append("yellow")
    green = lambda: order.append("green")
    brown = lambda: order.append("brown")

    pipeline = Pipeline()
    pipeline.add_task("blue", lambda: Func(blue))
    pipeline.add_task("red", lambda _: Func(red), dependencies=["blue"])
    pipeline.add_task("yellow", lambda _: Func(yellow), dependencies=["red"])
    pipeline.add_task("purple", lambda _, __: Func(purple), dependencies=["blue", "red"])
    pipeline.add_task("green", lambda _, __: Func(green), dependencies=["yellow", "blue"])
    pipeline.add_task("brown", lambda _, __: Func(brown), dependencies=["green", "purple"])

    asyncio.run(pipeline.run())

    assert order == ["blue", "red", "yellow", "purple", "green", "brown"]

def test_pipeline_each_dep_runs_once():
    # test that each dependency is only run once

    order = []

    blue = lambda: order.append("blue")
    red = lambda: order.append("red")
    yellow = lambda: order.append("yellow")
    green = lambda: order.append("green")

    pipeline = Pipeline()
    pipeline.add_task("blue", lambda: Func(blue))
    pipeline.add_task("red", lambda _: Func(red), dependencies=["blue"])
    pipeline.add_task("yellow", lambda _, __: Func(yellow), dependencies=["blue", "red"])
    pipeline.add_task("green", lambda _, __, ___: Func(green), dependencies=["blue", "red", "yellow"])

    asyncio.run(pipeline.run())

    assert order == ["blue", "red", "yellow", "green"]


def test_pipeline_data_transfer():
    # test that the data is transferred between tasks

    async def get_one():
        await asyncio.sleep(0.1)
        return 1

    def add_two(value):
        return value + 2

    def add_five(value):
        return value + 5

    pipeline = Pipeline()
    pipeline.add_task_async(
        "get_one",
        lambda: AsyncFunc(get_one)
    )
    pipeline.add_task(
        "add_two",
        lambda value: Func(add_two, value),
        dependencies=["get_one"]
    )
    pipeline.add_task(
        "add_five",
        lambda value: Func(add_five, value),
        dependencies=["add_two"]
    )

    results = asyncio.run(pipeline.run())

    assert results["get_one"] == 1
    assert results["add_two"] == 3
    assert results["add_five"] == 8


def test_pipelinedd_task_async():
    # test that the task is really async

    SMALL_WAIT = 0.05
    BIG_WAIT = 0.1

    BAD_VALUE = -1
    GOOD_VALUE = 200

    box = {"value": BAD_VALUE}

    async def set_value():
        await asyncio.sleep(SMALL_WAIT)
        box["value"] = GOOD_VALUE

    async def get_value():
        await asyncio.sleep(BIG_WAIT)
        return box["value"]

    pipeline = Pipeline()
    pipeline.add_task_async(
        "get_value",
        lambda: AsyncFunc(get_value)
    )

    async def run_pipelinend_set_value():
        # launch concurrently
        results = await asyncio.gather(
            pipeline.run(),
            set_value()
        )
        return results

    results, _ = asyncio.run(run_pipelinend_set_value())

    assert results["get_value"] == GOOD_VALUE

