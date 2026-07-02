<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Level Up Test</title>
    <!-- Подключаем Telegram Web App SDK -->
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { background-color: #0d1117; color: #ffffff; font-family: sans-serif; text-align: center; padding: 20px; }
        .btn { background-color: #238636; color: white; border: none; padding: 15px 30px; font-size: 18px; border-radius: 8px; margin-top: 20px; }
    </style>
</head>
<body>
    <h1 id="user-name">Загрузка...</h1>
    <p>Уровень: <span style="color: #238636; font-weight: bold;">LVL 1</span></p>
    <p>Твои запасы кофе: ☕ 0 шт.</p>
    
    <button class="btn" onclick="clickWheel()">Крутануть Колесо</button>

    <script>
        // Инициализируем Telegram Web App
        const tg = window.Telegram.WebApp;
        tg.ready(); // Сообщаем ТГ, что мини-апп готов

        // Берем имя пользователя прямо из его Телеграма!
        if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
            document.getElementById('user-name').innerText = "Привет, " + tg.initDataUnsafe.user.first_name + "!";
        } else {
            document.getElementById('user-name').innerText = "Привет, Гость!";
        }

        function clickWheel() {
            tg.showAlert("Барабан крутится! Выпал бонус: +3 рубля на баланс!");
        }
    </script>
</body>
</html>

