import unittest
from unittest.mock import patch

import gps_service
from yummy_app import YummyApp

# ======================================================================
# CAP DO 1: Bo test co ban cho san (ban dau chi dat ~35% Coverage)
# ======================================================================


class TestEasyLevel(unittest.TestCase):
    """Kiem thu chuc nang co ban: tinh tien don hang."""

    def setUp(self):
        self.app = YummyApp()

    def test_calculate_total_for_single_item(self):
        cart = {"pho": 2}
        self.assertEqual(self.app.calculate_order_total(cart), 100000)

    def test_calculate_total_for_multiple_items(self):
        cart = {"pho": 1, "bun": 1}
        self.assertEqual(self.app.calculate_order_total(cart), 95000)

    def test_calculate_total_for_empty_cart(self):
        self.assertEqual(self.app.calculate_order_total({}), 0.0)

    def test_calculate_total_with_zero_quantity(self):
        cart = {"pho": 0}
        self.assertEqual(self.app.calculate_order_total(cart), 0.0)


# ======================================================================
# CAP DO 2: Sinh vien tu tay lap trinh 2 class duoi day
# ======================================================================


class TestMediumLevel(unittest.TestCase):
    """Kiem thu ham apply_promo_code voi mock thuoc tinh
    network_status va os_version cua class YummyApp."""

    def test_apply_promo_online_valid(self):
        """(1) Online + ma hop le -> ap dung giam gia thanh cong."""
        app = YummyApp()
        with patch.object(app, "network_status", "online"), \
                patch.object(app, "os_version", 15):
            self.assertEqual(app.apply_promo_code(100000, "GIAM10"), 90000.0)

    def test_apply_promo_offline_raises_connection_error(self):
        """(2) Offline -> nem ConnectionError khi xac thuc ma."""
        app = YummyApp()
        with patch.object(app, "network_status", "offline"):
            with self.assertRaises(ConnectionError):
                app.apply_promo_code(100000, "GIAM10")

    def test_os_only_promo_on_os15_valid(self):
        """(3) Ma NEW_OS_ONLY tren OS 15 -> hop le, giam 20%."""
        app = YummyApp()
        with patch.object(app, "network_status", "online"), \
                patch.object(app, "os_version", 15):
            self.assertEqual(app.apply_promo_code(100000, "NEW_OS_ONLY"), 80000.0)

    def test_os_only_promo_on_os14_raises_value_error(self):
        """(4) Ma NEW_OS_ONLY tren OS 14 -> nem ValueError."""
        app = YummyApp()
        with patch.object(app, "network_status", "online"), \
                patch.object(app, "os_version", 14):
            with self.assertRaises(ValueError):
                app.apply_promo_code(100000, "NEW_OS_ONLY")


class TestHardLevel(unittest.TestCase):
    """Kiem thu ham get_nearby_restaurants voi mock phan cung GPS
    qua decorator @patch('yummy_app.gps_service.get_current_location')."""

    @patch("yummy_app.gps_service.get_current_location")
    def test_nearby_restaurants_in_zone(self, mock_get_location):
        """(1) Mock GPS tra ve toa do trong vung (10.0, 105.0)
        -> tra ra danh sach nha hang."""
        mock_get_location.return_value = (10.0, 105.0)
        app = YummyApp()
        self.assertEqual(
            app.get_nearby_restaurants(),
            ["Nha hang Pho Ly Quoc Su", "Bun cha Huong Lien"],
        )

    @patch("yummy_app.gps_service.get_current_location")
    def test_nearby_restaurants_out_of_zone(self, mock_get_location):
        """(2) Mock GPS tra ve toa do ngoai vung (20.0, 110.0)
        -> tra ra danh sach rong."""
        mock_get_location.return_value = (20.0, 110.0)
        app = YummyApp()
        self.assertEqual(app.get_nearby_restaurants(), [])

    @patch("yummy_app.gps_service.get_current_location")
    def test_nearby_restaurants_gps_signal_lost(self, mock_get_location):
        """(3) Mock GPS nem ngoai le GPSSignalLostError
        -> tra ve thong bao loi."""
        mock_get_location.side_effect = gps_service.GPSSignalLostError()
        app = YummyApp()
        self.assertEqual(
            app.get_nearby_restaurants(), "Khong the xac dinh vi tri."
        )


if __name__ == "__main__":
    unittest.main()
