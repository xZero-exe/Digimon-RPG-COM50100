"""Regresiones: portátiles, bandas del viewport y escala del eje temporal."""
import unittest
from digimon_rl.gui.layout import Viewport, episode_positions


class ViewportTests(unittest.TestCase):
    def test_content_fits_common_displays(self):
        for size in ((1366, 768), (1024, 768), (1920, 1080), (800, 600), (320, 240)):
            v = Viewport(*size)
            w, h = v.size
            self.assertLessEqual(w, size[0])
            self.assertLessEqual(h, size[1])
            self.assertAlmostEqual(w / h, 1280 / 820, delta=.01)

    def test_mouse_hits_same_button_after_scaling(self):
        for size in ((1366, 768), (800, 600), (1920, 1080)):
            v = Viewport(*size)
            ox, oy = v.origin
            w, h = v.size
            logical = v.to_logical((ox+round(500*w/1280), oy+round(600*h/820)))
            self.assertAlmostEqual(logical[0], 500, delta=2)
            self.assertAlmostEqual(logical[1], 600, delta=2)

    def test_black_bands_are_not_clickable(self):
        self.assertIsNone(Viewport(1920, 1080).to_logical((0, 0)))
        self.assertIsNone(Viewport(800, 600).to_logical((-1, 300)))

    def test_right_and_bottom_edges_excluded(self):
        v = Viewport(1280, 820)
        self.assertIsNone(v.to_logical((1280, 400)))
        self.assertIsNone(v.to_logical((600, 820)))
        self.assertEqual(v.to_logical((1279, 819)), (1279, 819))


class ChartAxisTests(unittest.TestCase):
    def test_distances_represent_episode_counts(self):
        xs = episode_positions((500, 2000, 5000, 10000, 20000), 0, 800)
        self.assertEqual(xs, (20, 80, 200, 400, 800))
        self.assertEqual((xs[-1]-xs[-2])/(xs[1]-xs[0]), 10000/1500)

    def test_one_checkpoint_and_invalid_order(self):
        self.assertEqual(episode_positions((500,), 10, 100), (110,))
        for values in ((), (0,), (500, 500), (2000, 500)):
            with self.assertRaises(ValueError):
                episode_positions(values, 0, 100)
