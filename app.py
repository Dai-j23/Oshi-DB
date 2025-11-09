from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import os

# 基本設定
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# データベース設計
class Talent(db.Model):
    # 主キー
    id = db.Column(db.Integer, primary_key=True)
    # タレント名(必須)
    name = db.Column(db.String(100), nullable=False)
    # 推しマーク
    oshi_mark = db.Column(db.String(50))
    # 所属
    affiliation = db.Column(db.String(100)) 
    # YoutubeチャンネルURL
    youtube_url = db.Column(db.String(200))
    # TwitterアカウントURL
    twitter_url = db.Column(db.String(200))

# メインページ
@app.route('/')
def index():
    # デフォルトを名前の昇順でソート
    talents = Talent.query.order_by(Talent.name.asc()).all()
    return render_template('index.html', talents=talents)

# データ登録
@app.route('/add', methods=['POST'])
def add_talent():
    # フォームデータの取得
    name = request.form['name']
    oshi_mark = request.form['oshi_mark']
    affiliation = request.form['affiliation']
    youtube_url = request.form['youtube_url']
    twitter_url = request.form['twitter_url']
    
    # インスタンス作成
    new_talent = Talent(
        name = name, 
        oshi_mark = oshi_mark,
        affiliation = affiliation, 
        youtube_url = youtube_url, 
        twitter_url = twitter_url
    )

    # インスタンスの保存
    db.session.add(new_talent)
    db.session.commit()
    
    # 登録した全データをJSONで返す
    return jsonify({
        'id': new_talent.id, 
        'name': new_talent.name, 
        'oshi_mark': new_talent.oshi_mark,
        'affiliation': new_talent.affiliation,
        'youtube_url': new_talent.youtube_url,
        'twitter_url': new_talent.twitter_url
    })

# データ更新
@app.route('/update/<int:talent_id>', methods=['POST'])
def update_talent(talent_id):
    try:
        talent_to_update = Talent.query.get_or_404(talent_id)
        
        # プロパティの更新
        talent_to_update.name = request.form['name']
        talent_to_update.oshi_mark = request.form['oshi_mark']
        talent_to_update.affiliation = request.form['affiliation']
        talent_to_update.youtube_url = request.form['youtube_url']
        talent_to_update.twitter_url = request.form['twitter_url']
        
        # 更新データの保存
        db.session.commit()
        
        # 更新後の全データをJSONで返す
        return jsonify({
            'id': talent_to_update.id, 
            'name': talent_to_update.name, 
            'oshi_mark': talent_to_update.oshi_mark,
            'affiliation': talent_to_update.affiliation,
            'youtube_url': talent_to_update.youtube_url,
            'twitter_url': talent_to_update.twitter_url
        })
    except:
        # ロールバック
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Update failed'}), 500

# データ削除
@app.route('/delete/<int:talent_id>', methods=['DELETE'])
def delete_talent(talent_id):
    try:
        talent_to_delete = Talent.query.get_or_404(talent_id)

        # 対象データの削除
        db.session.delete(talent_to_delete)

        #　削除結果の保存
        db.session.commit()

        # 削除成功のステータスをJSONで返す
        return jsonify({'status': 'success', 'message': 'Talent deleted'})

    except:
        # ロールバック
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Delete failed'}), 500

# 検索機能
@app.route('/search')
def search():
    # デフォルト値、空文字
    query_term = request.args.get('q', '') 

    if not query_term:
        talents_query = Talent.query.all()
    else:
        # LIKE演算子を利用するため'%'で挟む
        search_pattern = f"%{query_term}%"

        # 部分一致検索
        talents_query = Talent.query.filter(
            or_(
                Talent.name.like(search_pattern),
                Talent.affiliation.like(search_pattern),
                Talent.oshi_mark.like(search_pattern)
            )
        ).all()
    
    # JSONとして返却できる形式 (辞書のリスト) に変換
    talents_list = []
    for talent in talents_query:
        talents_list.append({
            'id': talent.id,
            'name': talent.name,
            'oshi_mark': talent.oshi_mark,
            'affiliation': talent.affiliation,
            'youtube_url': talent.youtube_url,
            'twitter_url': talent.twitter_url
        })
        
    return jsonify(talents_list)

# 実行
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Flaskの開発用サーバーを起動
    # debug=True に設定すると、コード変更時にサーバーが自動的に再起動
    app.run(debug=True)