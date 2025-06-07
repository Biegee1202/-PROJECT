import itertools
import random
from flask import Flask, request, jsonify, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging
import re

# 設置日誌記錄
logging.basicConfig(level=logging.DEBUG)

# 初始化 Flask 應用
app = Flask(__name__)
app.secret_key = 'your-fixed-secret-key'
CORS(app)

# 設定 SQLite 資料庫
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eat project .sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化資料庫
db = SQLAlchemy(app)

# 定義使用者模型
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<User {self.email}>'

# 定義餐點模型
class Meal(db.Model):
    __tablename__ = 'meals'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    meal_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Meal {self.meal_name}>'

# 定義菜品模型
class Dish(db.Model):
    __tablename__ = 'dishes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    calories = db.Column(db.Integer)
    protein = db.Column(db.Integer)
    fat = db.Column(db.Integer)

    def __repr__(self):
        return f'<Dish {self.name}>'

# 首頁路由
@app.route('/')
def index():
    logging.debug("正在渲染 meal2.html")
    return render_template('meal2.html')

# 登出路由
@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    logging.debug("用戶已登出")
    return jsonify({'success': True, 'message': '已成功登出'})

# 檢查 session 路由（用於除錯）
@app.route('/api/session', methods=['GET'])
def check_session():
    return jsonify({'user_id': session.get('user_id')})

# 登入路由
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
    except Exception as e:
        logging.error(f"無效的 JSON 資料: {str(e)}")
        return jsonify({'success': False, 'message': '無效的請求資料'}), 400

    email = data.get('email')
    password = data.get('password')

    logging.debug(f"登入嘗試: email={email}, password={password}")

    if not email or not password:
        return jsonify({'success': False, 'message': '請提供帳號和密碼'}), 400

    user = User.query.filter_by(email=email).first()

    if user and user.password == password:
        session['user_id'] = user.id
        logging.debug(f"登入成功: user_id={user.id}")
        return jsonify({'success': True, 'message': '登入成功'})
    
    logging.debug("登入失敗: 帳號或密碼錯誤")
    return jsonify({'success': False, 'message': '帳號或密碼錯誤'}), 401

# 註冊路由
@app.route('/api/register', methods=['POST'])
def register():
    if not request.is_json:
        logging.error("請求格式錯誤，非 JSON")
        return jsonify({'success': False, 'message': '請求格式錯誤，請使用 JSON 格式'}), 400

    try:
        data = request.get_json()
    except Exception as e:
        logging.error(f"無效的 JSON 資料: {str(e)}")
        return jsonify({'success': False, 'message': '無效的請求資料'}), 400

    email = data.get('email')
    password = data.get('password')

    logging.debug(f"註冊嘗試: email={email}, password={password}")

    if not email or not password or email.strip() == "":
        return jsonify({'success': False, 'message': '請提供有效的帳號和密碼'}), 400

    if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
        return jsonify({'success': False, 'message': '請提供有效的電子郵件格式'}), 400

    if not isinstance(password, str) or not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$', password):
        return jsonify({'success': False, 'message': '密碼至少需要6個字符，且包含字母和數字'}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        logging.debug("註冊失敗: 帳號已存在")
        return jsonify({'success': False, 'message': '此帳號已被註冊'}), 400

    new_user = User(email=email, password=password)

    try:
        db.session.add(new_user)
        db.session.commit()
        logging.debug(f"註冊成功: email={email}")
        return jsonify({'success': True, 'message': '註冊成功'})
    except IntegrityError as ex:
        db.session.rollback()
        logging.error(f"註冊失敗 (IntegrityError): {str(ex)}")
        return jsonify({'success': False, 'message': '註冊失敗：此電子郵件已被使用'}), 400
    except SQLAlchemyError as ex:
        db.session.rollback()
        logging.error(f"註冊失敗 (SQLAlchemyError): {str(ex)}")
        return jsonify({'success': False, 'message': '註冊失敗：資料庫錯誤，請稍後再試'}), 500

# 新增餐點路由
@app.route('/api/meals', methods=['POST'])
def add_meal():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '請先登入'}), 401

    data = request.get_json()
    meal_name = data.get('meal_name')

    if not meal_name:
        return jsonify({'success': False, 'message': '請提供餐點名稱'}), 400

    try:
        new_meal = Meal(user_id=session['user_id'], meal_name=meal_name)
        db.session.add(new_meal)
        db.session.commit()
        logging.debug(f"餐點新增成功: meal_name={meal_name}")
        return jsonify({'success': True, 'message': '餐點已新增', 'meal_id': new_meal.id})
    except IntegrityError as ex:
        db.session.rollback()
        logging.error(f"新增餐點失敗 (IntegrityError): {str(ex)}")
        return jsonify({'success': False, 'message': '新增餐點失敗：數據衝突'}), 400
    except SQLAlchemyError as ex:
        db.session.rollback()
        logging.error(f"新增餐點失敗 (SQLAlchemyError): {str(ex)}")
        return jsonify({'success': False, 'message': '新增餐點失敗：資料庫錯誤，請稍後再試'}), 500

# 獲取使用者的所有餐點
@app.route('/api/meals', methods=['GET'])
def get_meals():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '請先登入'}), 401

    meals = Meal.query.filter_by(user_id=session['user_id']).all()
    meals_list = [{'id': meal.id, 'name': meal.meal_name, 'created_at': meal.created_at.isoformat()} for meal in meals]
    return jsonify({'success': True, 'meals': meals_list})

# 獲取所有菜品
@app.route('/api/dishes', methods=['GET'])
def get_dishes():
    dishes = Dish.query.limit(10).all()
    dishes_list = [{
        'id': dish.id,
        'name': dish.name,
        'price': dish.price,
        'calories': dish.calories,
        'protein': dish.protein,
        'fat': dish.fat
    } for dish in dishes]
    return jsonify({'success': True, 'dishes': dishes_list})

# 網頁顯示菜品
@app.route('/dishes')
def dishes():
    dishes = Dish.query.limit(10).all()
    return render_template('meal2.html', dishes=dishes)

@app.route('/api/recommend', methods=['POST'])
def recommend_meals():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '請提供條件資料'}), 400

    max_price = data.get('max_price', 400)
    max_calories = data.get('max_calories', 2000)
    min_protein = data.get('min_protein', 60)
    

    # 從資料庫撈出全部菜品（可調整條件）
    dishes = Dish.query.all()




 # 篩出符合條件的單道菜
    valid_dishes = [{
        'id': d.id,
        'name': d.name,
        'price': d.price,
        'calories': d.calories,
        'protein': d.protein
    } for d in dishes if (
        d.price is not None and
        d.calories is not None and
        d.protein is not None and
        d.price <= max_price and
        d.calories <= max_calories and
        d.protein >= min_protein
    )]

    if not valid_dishes:
        return jsonify({'success': False, 'message': '抱歉，沒有符合條件的菜品'}), 200

    return jsonify({'success': True, 'results': valid_dishes})

    # 隨機抽幾組
    # sampled = random.sample(valid_combos, min(result_count, len(valid_combos)))
    # return jsonify({'success': True, 'results': sampled})

@app.route('/menu.html')
def show_menu_page():
    return render_template('menu.html')

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            logging.debug("資料庫表創建成功")
        except Exception as e:
            logging.error(f"資料庫初始化失敗: {str(e)}")
    app.run(debug=True)

# import os
# print("📂 正在使用的資料庫位置：", os.path.abspath('eat project .sqlite'))

# with app.app_context():
#     print("📊 dishes 表目前筆數：", Dish.query.count())




