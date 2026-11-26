from fastapi.testclient import TestClient

from tests.helpers import complete_setup


def test_settings_defaults_and_update(authed: TestClient) -> None:
    current = authed.get("/api/v1/settings").json()
    assert current["display_currency"] == "USD"
    assert current["retention"]["expired_job_days"] == 180

    current["new_job_window_days"] = 14
    current["freshness"] = {"pathway_fresh_days": 90, "pathway_outdated_days": 400}
    assert authed.put("/api/v1/settings", json=current).status_code == 200
    assert authed.get("/api/v1/settings").json()["new_job_window_days"] == 14


def test_settings_validation(authed: TestClient) -> None:
    current = authed.get("/api/v1/settings").json()
    bad = {
        **current,
        "default_page_size": 25,
        "display_currency": "usd",
        "freshness": {"pathway_fresh_days": 400, "pathway_outdated_days": 300},
    }
    response = authed.put("/api/v1/settings", json=bad)
    assert response.status_code == 422
    fields = {d["field"] for d in response.json()["error"]["details"]}
    assert {"default_page_size", "display_currency", "freshness"} <= fields


def test_profile_version_bumps_only_on_scoring_changes(authed: TestClient) -> None:
    start = authed.get("/api/v1/profile").json()["profile_version"]

    renamed = authed.patch("/api/v1/profile", json={"full_name": "New Name"}).json()
    assert renamed["full_name"] == "New Name"
    assert renamed["profile_version"] == start

    moved = authed.patch(
        "/api/v1/profile",
        json={
            "residence_country_code": "DE",
            "citizenships": [{"country_code": "PK", "is_primary": True}],
        },
    ).json()
    assert moved["residence_country_code"] == "DE"
    assert moved["profile_version"] == start + 1

    dual = authed.patch(
        "/api/v1/profile",
        json={"citizenships": [{"country_code": "PK", "is_primary": True}, {"country_code": "GB"}]},
    ).json()
    assert [c["country_code"] for c in dual["citizenships"]] == ["PK", "GB"]
    assert dual["profile_version"] == start + 2


def test_profile_validation(authed: TestClient) -> None:
    duplicate = authed.patch(
        "/api/v1/profile", json={"citizenships": [{"country_code": "PK"}, {"country_code": "PK"}]}
    )
    assert duplicate.status_code == 422

    unknown = authed.patch("/api/v1/profile", json={"residence_country_code": "ZZ"})
    assert unknown.status_code == 422
    assert unknown.json()["error"]["details"][0]["code"] == "unknown_country"


def test_countries_list_search_region_and_sort(authed: TestClient) -> None:
    page = authed.get("/api/v1/countries").json()
    assert page["total"] == 249
    assert page["page_size"] == 20
    assert page["items"][0]["name"] == "Afghanistan"

    assert [c["code"] for c in authed.get("/api/v1/countries?q=pakis").json()["items"]] == ["PK"]
    assert authed.get("/api/v1/countries?region=EU").json()["total"] == 27
    assert authed.get("/api/v1/countries?region=GCC,EU").json()["total"] == 33
    assert authed.get("/api/v1/countries?sort=-name").json()["items"][0]["code"] == "AX"

    invalid = authed.get("/api/v1/countries?sort=population")
    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "invalid_sort"


def test_country_detail(authed: TestClient) -> None:
    germany = authed.get("/api/v1/countries/de").json()
    assert germany["name"] == "Germany"
    assert germany["english_status"] == "unknown"
    assert {"EU", "EEA", "EUROPE", "EMEA"} <= set(germany["region_codes"])

    missing = authed.get("/api/v1/countries/zz")
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "not_found"


def test_country_options_are_public_only_until_setup(client: TestClient) -> None:
    options = client.get("/api/v1/countries/options").json()
    assert len(options) == 249
    assert {"code": "PK", "name": "Pakistan"} in options

    complete_setup(client)
    assert client.get("/api/v1/countries/options").status_code == 200
    client.cookies.clear()
    assert client.get("/api/v1/countries/options").status_code == 401
