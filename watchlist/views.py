from flask import Flask,render_template, request, url_for, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user

from watchlist import app, db
from watchlist.models import User, Movie, Actor, movie_actor

@app.route('/', methods=['GET', 'POST'])
def index():
    # 获取排序参数，默认按照年份升序排序
    sort_order = request.args.get('sort_order', 'asc')

    # 查询数据库，获取符合条件的电影
    movies = Movie.query.order_by(Movie.year.asc() if sort_order == 'asc' else Movie.year.desc()).all()

    # 处理分页显示电影的逻辑
    movies_per_page = 15  # 每页显示的电影数量
    page = int(request.args.get('page', 1))
    start_index = (page - 1) * movies_per_page
    end_index = start_index + movies_per_page
    current_movies = movies[start_index:end_index]
    total_pages = (len(movies) + movies_per_page - 1) // movies_per_page

    return render_template('index.html', movies=movies, current_movies=current_movies, page=page, total_pages=total_pages)


@app.route('/add_movie', methods=['GET', 'POST']) # 手动录入电影
@login_required
def add_movie():
        if request.method == 'POST':
            title = request.form['title']
            year = request.form['year']
            date = request.form['date']
            country = request.form['country']
            type = request.form['type']
            box = request.form['box']

            if not title or not year or len(year) != 4 or len(title) > 60 or not date or not country or not type:
                flash('请检查输入.')
                return redirect(url_for('add_movie'))

            movie = Movie(title=title, year=year, date=date, country=country, type=type, box=box)
            db.session.add(movie)
            db.session.commit()
            flash('已录入电影条目.')
            return redirect(url_for('index'))

        return render_template('add_movie.html', current_user=current_user)


@app.route('/filter_movies', methods=['POST'])  # 筛选电影
def filter_movies():
    filter_title = request.form.get('filter_title')
    movies = Movie.query.all()
    page = int(request.args.get('page', 1))

    # 查询数据库，获取符合条件的电影
    if filter_title:
        filtered_movies = Movie.query.filter(Movie.title.ilike(f'%{filter_title}%')).all()
    else:
        filtered_movies = Movie.query.all()

    # 处理分页显示电影的逻辑
    movies_per_page = 15  # 每页显示的电影数量
    start_index = (page - 1) * movies_per_page
    end_index = start_index + movies_per_page
    current_filtered_movies = filtered_movies[start_index:end_index]
    total_pages = (len(filtered_movies) + movies_per_page - 1) // movies_per_page

    return render_template('index.html', movies=filtered_movies, current_movies=current_filtered_movies, page=page,
                           total_pages=total_pages)


@app.route('/movie_details/<int:movie_id>')  # 详细信息查询
@login_required
def movie_details(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    movie_actor_info = db.session.query(movie_actor).filter_by(movie_id=movie_id).all() # 查询关联表，获取导演和主演信息

    director_id = [actor.actor_id for actor in movie_actor_info if actor.role == '导演']
    main_actor_ids = [actor.actor_id for actor in movie_actor_info if actor.role == '主演']

    # 查询导演和主演的详细信息
    director = Actor.query.get(director_id[0]) if director_id else None
    main_actors = Actor.query.filter(Actor.actor_id.in_(main_actor_ids)).all()

    return render_template('movie_details.html', movie=movie, director=director, main_actors=main_actors)


@app.route('/search_actor', methods=['GET'])  # 演员查询
def search_actor():
    actor_name = request.args.get('actor_name')
    actor = Actor.query.filter_by(actor_name=actor_name).first_or_404()  # 演员信息

    actor_movie_info = db.session.query(movie_actor).filter(movie_actor.c.actor_id == actor.actor_id).all()

    movie_director_ids = [movie.movie_id for movie in actor_movie_info if movie.role == '导演']
    movie_main_actor_ids = [movie.movie_id for movie in actor_movie_info if movie.role == '主演']

    movie_directors = Movie.query.filter(Movie.movie_id.in_(movie_director_ids)).all()
    movie_main_actors = Movie.query.filter(Movie.movie_id.in_(movie_main_actor_ids)).all()

    return render_template('actor_details.html', actor=actor, movie_directors=movie_directors,
                           movie_main_actors=movie_main_actors)


@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])  # 编辑电影
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':  # 处理编辑表单的提交请求
        title = request.form['title']
        year = request.form['year']
        date = request.form['date']
        country = request.form['country']
        type = request.form['type']
        box=request.form['box']

        if not title or not year or len(year) != 4 or len(title) > 60 or not date or not country or not type:  # 服务器端追加认证
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))  # 重定向编辑界面

        movie.title = title
        movie.year = year
        movie.date=date
        movie.country=country
        movie.type=type
        movie.box=box
        db.session.commit()  # 提交数据库会话
        flash('条目更新完成.')
        return redirect(url_for('index'))  # 重定向主页

    return render_template('edit.html', movie=movie)  # 传入被编辑的电影记录


@app.route('/movie/delete/<int:movie_id>', methods=['POST'])  # 删除电影记录
@login_required
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)  # 获取电影记录
    db.session.delete(movie)  # 删除电影记录
    db.session.commit()  # 提交数据库会话
    flash('Item deleted.')
    return redirect(url_for('index'))  # 重定向主页


@app.route('/settings', methods=['GET', 'POST'])  # 修改用户名
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('请检查输入.')
            return redirect(url_for('settings'))

        user = User.query.first()
        user.name = name
        db.session.commit()
        flash('重命名完成.')
        return redirect(url_for('index'))

    return render_template('settings.html')


@app.route('/login', methods=['GET', 'POST'])  # 登录操作
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('请检查输入.')
            return redirect(url_for('login'))

        user = User.query.first()

        if username == user.username and user.validate_password(password):
            login_user(user)
            flash('登陆成功.')
            return redirect(url_for('index'))

        flash('密码错误，请检查用户名或密码。')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')   # 登出操作
@login_required
def logout():
    logout_user()
    flash('Goodbye.')
    return redirect(url_for('index'))
