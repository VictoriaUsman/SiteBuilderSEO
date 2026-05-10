import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from seo.linking import InternalLinkGraph


def test_same_service_links():
    g = InternalLinkGraph()
    g.add_page("roof-repair-dallas", "Roof Repair", "Dallas", "roof repair")
    g.add_page("roof-repair-austin", "Roof Repair", "Austin", "roof repair")
    g.add_page("plumbing-dallas", "Plumbing", "Dallas", "plumber")
    g.build_links()

    links = g.get_links_for("roof-repair-dallas")
    assert "roof-repair-austin" in links


def test_same_city_links():
    g = InternalLinkGraph()
    g.add_page("roof-repair-dallas", "Roof Repair", "Dallas", "roof repair")
    g.add_page("plumbing-dallas", "Plumbing", "Dallas", "plumber")
    g.build_links()

    links = g.get_links_for("roof-repair-dallas")
    assert "plumbing-dallas" in links


def test_no_self_links():
    g = InternalLinkGraph()
    g.add_page("roof-repair-dallas", "Roof Repair", "Dallas", "roof repair")
    g.build_links()

    links = g.get_links_for("roof-repair-dallas")
    assert "roof-repair-dallas" not in links


def test_summary():
    g = InternalLinkGraph()
    g.add_page("roof-repair-dallas", "Roof Repair", "Dallas", "roof repair")
    g.add_page("roof-repair-austin", "Roof Repair", "Austin", "roof repair")
    g.build_links()

    s = g.summary()
    assert s["total_pages"] == 2
    assert s["total_links"] == 2
