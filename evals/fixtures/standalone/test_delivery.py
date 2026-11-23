import unittest

from delivery import submit


class DeliveryTest(unittest.TestCase):
    def test_returns_receipt_on_success(self):
        self.assertEqual(submit("toy", lambda _: "receipt"), {
            "status": "submitted", "receipt": "receipt",
        })

    def test_does_not_resend_after_timeout(self):
        seen = []

        def send(document):
            seen.append(document)
            raise TimeoutError

        result = submit("toy", send)
        self.assertEqual(seen, ["toy"])
        self.assertEqual(result, {"status": "pending_confirmation", "receipt": None})
