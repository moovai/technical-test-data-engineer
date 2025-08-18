from data_ingestion import fetch_data as fetch

def test_iter_pages_paginates(fake_session):
    # match the signature used by iter_pages
    def fake_get(url, params=None, timeout=None):
        page = params["page"]
        if page == 1:
            return fake_session.FakeResp({
                "items": [{"id": 1, "updated_at": "2025-08-01T00:00:00"}],
                "pages": 2
            })
        elif page == 2:
            return fake_session.FakeResp({
                "items": [{"id": 2, "updated_at": "2025-08-02T00:00:00"}],
                "pages": 2
            })
        else:
            raise AssertionError("Should not request page > 2")

    fake_session.get = fake_get

    # run
    pages = list(fetch.iter_pages("tracks", size=100))

    # assert
    assert len(pages) == 2
    assert pages[0]["items"][0]["id"] == 1
    assert pages[1]["items"][0]["id"] == 2