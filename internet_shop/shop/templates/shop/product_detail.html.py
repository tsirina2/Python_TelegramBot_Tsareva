<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>{{ product.name }}</title>
</head>
<body>
    <h1>{{ product.name }}</h1>
    <p><b>Цена:</b> {{ product.price }} ₽</p>
    <p>{{ product.description }}</p>
    {% if product.image %}
        <img src="{{ product.image.url }}" alt="{{ product.name }}" width="300">
    {% endif %}
    <p><a href="{% url 'shop:product_list' %}">← Назад к списку</a></p>
</body>
</html>