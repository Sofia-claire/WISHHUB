from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from datetime import datetime
import secrets  # для генерации секретных ключей
from urllib.parse import urlparse

#  НАСТРОЙКА FLASK 
application = Flask(__name__)
application.secret_key = 'ваш-секретный-ключ-смените-это'

# Хранилище вишлистов
WISHLISTS = []  # каждый вишлист: {'id', 'name', 'items', 'secret_key', 'created_at'}

# ФУНКЦИИ 
def is_valid_url(url):
    if not url:
        return True
    try:
        result = urlparse(url)
        return all([result.scheme in ('http', 'https'), result.netloc])
    except:
        return False

def is_valid_price(price):
    if not price:
        return False
    # разрешаем числа с пробелами и ₽ в конце
    import re
    return re.match(r'^\d+(\s?\d+)*\s?₽?$', price.strip()) is not None

# МАРШРУТЫ 
# Главная: создание нового вишлиста
@application.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name', 'Мой вишлист')
        secret_key = secrets.token_urlsafe(16)
        wishlist_id = len(WISHLISTS) + 1
        
        new_wishlist = {
            'id': wishlist_id,
            'name': name,
            'items': [],
            'secret_key': secret_key,
            'created_at': datetime.now().strftime('%d.%m.%Y %H:%M')
        }
        WISHLISTS.append(new_wishlist)
        return redirect(url_for('edit_wishlist', wishlist_id=wishlist_id, key=secret_key))
    
    for w in WISHLISTS:
        if not isinstance(w.get('items'), list):
            w['items'] = []
    
    return render_template('create_wishlist.html', wishlists=WISHLISTS)

# Просмотр (публичная ссылка)
@application.route('/wishlist/<int:wishlist_id>')
def view_wishlist(wishlist_id):
    wishlist = next((w for w in WISHLISTS if w['id'] == wishlist_id), None)
    if not wishlist:
        return "Список не найден", 404
    if not isinstance(wishlist.get('items'), list):
        wishlist['items'] = []
    return render_template('index.html', items=wishlist['items'], editable=False, wishlist=wishlist)

# Редактирование (приватная ссылка)
@application.route('/wishlist/<int:wishlist_id>/edit', methods=['GET', 'POST'])
def edit_wishlist(wishlist_id):
    key = request.args.get('key')
    wishlist = next((w for w in WISHLISTS if w['id'] == wishlist_id), None)
    if not wishlist or key != wishlist['secret_key']:
        return "Доступ запрещен", 403
    if not isinstance(wishlist.get('items'), list):
        wishlist['items'] = []

    if request.method == 'POST':
        data = request.json
        name = data.get('name', 'Новый товар')
        price = data.get('price', '0 ₽')
        image = data.get('image', '')
        source_url = data.get('source_url', '')
        description = data.get('description', '')

        # Валидация
        if not name.strip():
            return jsonify({'success': False, 'error': 'Название обязательно'})
        if not is_valid_price(price):
            return jsonify({'success': False, 'error': 'Некорректная цена'})
        if not is_valid_url(image):
            return jsonify({'success': False, 'error': 'Некорректная ссылка на изображение'})
        if not is_valid_url(source_url):
            return jsonify({'success': False, 'error': 'Некорректная ссылка на товар'})

        new_item = {
            'id': len(wishlist['items']) + 1,
            'name': name.strip(),
            'price': price.strip(),
            'image': image.strip(),
            'source_url': source_url.strip(),
            'description': description.strip(),
            'added_date': datetime.now().strftime('%d.%m.%Y %H:%M'),
            'parsed': False
        }
        wishlist['items'].append(new_item)
        return jsonify({'success': True, 'item': new_item})

    return render_template('index.html', items=wishlist['items'], editable=True, wishlist=wishlist)

# Удаление товара из приватного списка
@application.route('/wishlist/<int:wishlist_id>/delete/<int:item_id>', methods=['DELETE'])
def delete_item(wishlist_id, item_id):
    key = request.args.get('key')
    wishlist = next((w for w in WISHLISTS if w['id'] == wishlist_id), None)
    if not wishlist or key != wishlist['secret_key']:
        return jsonify({'error': 'Доступ запрещен'}), 403
    if not isinstance(wishlist.get('items'), list):
        wishlist['items'] = []
    
    wishlist['items'] = [item for item in wishlist['items'] if item['id'] != item_id]
    return jsonify({'success': True})

# ЗАПУСК СЕРВЕРА 
if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("=" * 50)
    print("🚀 WishHub MVP запускается...")
    print("📁 Папки: templates/, static/")
    print("🌐 Откройте: http://localhost:5000")
    print("=" * 50)
    application.run(debug=True, host='0.0.0.0', port=5000)

#проверка коммитов
