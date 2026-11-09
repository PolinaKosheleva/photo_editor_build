"""Модуль фильтров для фоторедактора."""

import cv2


def apply_grayscale(image):
    """Применить фильтр «Оттенки серого».

    Результат возвращается в BGR (3 канала), чтобы его можно было
    отображать и сохранять так же, как цветное изображение.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
