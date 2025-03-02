from flask import Flask, render_template, abort
from markupsafe import Markup
import os
import markdown
import datetime
import glob

app = Flask(__name__)

def get_blog_posts():
    posts = []
    blog_dir = os.path.join(os.path.dirname(__file__), "blog_posts")
    
    os.makedirs(blog_dir, exist_ok=True)
    
    for md_file in glob.glob(os.path.join(blog_dir, "*.md")):
        filename = os.path.basename(md_file)
        slug = os.path.splitext(filename)[0]
        
        with open(md_file, 'r') as file:
            content = file.read()
        
        if content.startswith('---'):
            end_frontmatter = content.find('---', 3)
            if end_frontmatter != -1:
                frontmatter = content[3:end_frontmatter].strip()
                content = content[end_frontmatter + 3:].strip()
                
                meta = {}
                for line in frontmatter.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        meta[key.strip()] = value.strip()
        else:
            meta = {}
        
        html_content = Markup(markdown.markdown(content))
        
        title = meta.get('title', slug.replace('-', ' ').title())
        
        date_str = meta.get('date')
        if date_str:
            try:
                date = datetime.datetime.strptime(date_str, '%Y-%m-%d').strftime('%B %d, %Y')
            except ValueError:
                date = datetime.datetime.fromtimestamp(os.path.getmtime(md_file)).strftime('%B %d, %Y')
        else:
            date = datetime.datetime.fromtimestamp(os.path.getmtime(md_file)).strftime('%B %d, %Y')
        
        summary = meta.get('summary', html_content[:100].replace('<p>', '').replace('</p>', '') + '...')
        
        categories = meta.get('categories', '').split(',')
        categories = [cat.strip() for cat in categories if cat.strip()]
        
        image = meta.get('image', '')
        
        posts.append({
            'slug': slug,
            'title': title,
            'date': date,
            'content': html_content,
            'summary': summary,
            'categories': categories,
            'image': image
        })
    
    posts.sort(key=lambda x: x['date'], reverse=True)
    return posts

# Sample portfolio projects
def get_portfolio_projects():
    return [
        {
            'slug': 'project-one',
            'title': 'Project One',
            'description': 'A sample project description.',
            'image': 'https://via.placeholder.com/300x200'
        },
        {
            'slug': 'project-two',
            'title': 'Project Two',
            'description': 'Another sample project description.',
            'image': 'https://via.placeholder.com/300x200'
        },
        {
            'slug': 'project-three',
            'title': 'Project Three',
            'description': 'Yet another sample project description.',
            'image': 'https://via.placeholder.com/300x200'
        }
    ]

@app.template_filter('now')
def _jinja2_filter_now(format_string):
    if format_string == 'year':
        return datetime.datetime.now().year
    return datetime.datetime.now().strftime(format_string)

@app.route("/")
def home():
    blog_posts = get_blog_posts()[:3]  # Get 3 most recent posts
    projects = get_portfolio_projects()[:3]  # Get 3 projects
    
    return render_template('home.html', recent_posts=blog_posts, recent_projects=projects)

@app.route("/blog")
def blog_list():
    blog_posts = get_blog_posts()
    return render_template('blog/blogList.html', blog_posts=blog_posts)

@app.route("/blog/<slug>")
def blog_post(slug):
    blog_posts = get_blog_posts()
    
    post = next((p for p in blog_posts if p['slug'] == slug), None)
    
    if not post:
        abort(404)
    
    current_index = blog_posts.index(post)
    prev_post = blog_posts[current_index + 1] if current_index + 1 < len(blog_posts) else None
    next_post = blog_posts[current_index - 1] if current_index > 0 else None
    
    return render_template('blog/blogPostView.html', post=post, prev_post=prev_post, next_post=next_post)

@app.route("/portfolio")
def portfolio_list():
    projects = get_portfolio_projects()
    return render_template('portfolio/portfolioList.html', projects=projects)

if __name__ == "__main__":
    app.run(debug=True)