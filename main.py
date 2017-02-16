#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2, cgi, jinja2, os, re, time
from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))


class Blogpost(db.Model):
    title = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add = True)
    text = db.TextProperty()

class Handler(webapp2.RequestHandler):
    def renderError(self, error_code):
        self.error(error_code)
        self.response.write("Something's wrong! Help!")

class Index(Handler):
    def get(self):
        self.redirect("/blog")

class Blog(Handler):
    def get(self):
        blogs = db.GqlQuery("SELECT * FROM Blogpost ORDER BY created DESC LIMIT 5")
        t = jinja_env.get_template("main-blog.html")
        content = t.render(blogs = blogs)
        self.response.write(content)

class NewPost(Handler):
    def write_form(self, new_blog_title, new_blog_body, error):
        t = jinja_env.get_template("new-post.html")
        content = t.render()
        self.response.write(content)

    def get(self):
        self.write_form(new_blog_title="", new_blog_body="", error="")

    def post(self):
        new_blog_title = self.request.get("title")
        new_blog_body = self.request.get("text")
        have_error = False

        if (not new_blog_title) or (new_blog_title.strip() == ""):
            have_error = True
            error = "Please give your blog a title."
        else:
            error = ""

        if (not new_blog_body) or (new_blog_body.strip() == ""):
            have_error = True
            error = "Please write something."


        if not have_error:

            blogpost = Blogpost(title = new_blog_title, text = new_blog_body)
            blogpost.put()

            self.redirect("/blog/%s" % str(blogpost.key().id()))
        else:
            t = jinja_env.get_template("new-post.html")
            content = t.render(new_blog_title=new_blog_title, new_blog_body=new_blog_body, error=error)
            self.response.write(content)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        blog_key = db.Key.from_path('Blogpost', int(id))
        blog_post = db.get(blog_key)

        if not blog_post:
            self.error(404)
            return

        t=jinja_env.get_template("post.html")
        content = t.render(blog_post = blog_post)
        self.response.write(content)


app = webapp2.WSGIApplication([
    ('/', Index),
    ('/blog', Blog),
    ('/new-post', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
