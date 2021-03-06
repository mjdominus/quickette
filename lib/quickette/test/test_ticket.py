
from quickette.ticket import Ticket, TicketMeta
from datetime import datetime
import pytest
import sys

def test_parse(sample_ticket_text):
    t = Ticket.load_from_array(sample_ticket_text.splitlines())

    # lowercasing of field names
    assert t.header["id"] == "142857"
    assert t.header["title"] == "sample ticket"

    # conversions
    assert t.header["created"] == datetime.fromisoformat("2020-04-02T02:38:00")

    # Hyphens in the key, spaces in the value
    assert t.header["favorite-food"] == "crab cakes"

    # Default status
    assert t.header["status"] == "ready"

    with pytest.raises(KeyError):
        t.header["poo"]

    assert t.body == [ "This is a ticket body.", "", "It has two sections." ]

    assert t.file is None

def test___str__(sample_ticket_text):
    # Also tests Ticket.load_from_string and round-tripping of dump-then-parse
    t1 = Ticket.load_from_array(sample_ticket_text.splitlines())
    t2 = Ticket.load_from_string(str(t1))

    assert str(t2) == str(t1)

def test_no_body():
    t1 = Ticket(TicketMeta(id=1, title="foo"))
    assert t1.body == ""

def test_subtickets():
    def tkt(n):
        return Ticket(TicketMeta(ID=n, title=f"ticket {n}"))
    t1, t2 = tkt(1), tkt(2)

    t1.add_subticket(t2)
    assert t2.parent == t1
    assert t1.all_subtickets() == set([ t1, t2 ])
    assert t2.all_subtickets() == set([ t2 ])

    t3, t4 = tkt(3), tkt(4)
    t1.add_subticket(t3)
    t2.add_subticket(t4)
    assert t1.subtickets == set([t2, t3])
    assert t2.subtickets == set([t4])
    assert t3.subtickets == set()
    assert t4.subtickets == set()

    assert t1.parent is None
    assert t2.parent == t1
    assert t3.parent == t1
    assert t4.parent == t2

    assert t1.all_subtickets() == set([t1, t2, t3, t4])
    assert t2.all_subtickets() == set([t2, t4])
    assert t3.all_subtickets() == set([t3])
    assert t4.all_subtickets() == set([t4])

    for t in t1, t2, t3, t4:
        assert t.root() == t1
        assert t.relatives() == set([t1, t2, t3, t4])

def test_filename():
    tests = [ ("sample ticket", "sample-ticket.md"),
              ("Sample Ticket", "sample-ticket.md"),
              ("ticket #2", "ticket-2.md"),
              ("sample    ticket", "sample-ticket.md"),
              ("fix broken `Penguin` class",
               "fix-broken-penguin-class.md"),
              ]

    for title, x in tests:
        a = Ticket.generate_filename(title)
        assert a == x
