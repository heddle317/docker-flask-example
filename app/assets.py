from app import app
from app import config

from flask_assets import Bundle
from flask_assets import Environment


assets = Environment(app)


base_css = Bundle('css/external/bootstrap.min.css',
                  'css/external/bootstrap-theme.min.css',
                  'css/external/font-awesome.min.css',
                  filters='cssmin', output='gen/base.%(version)s.css')

assets.register('base_css', base_css)

if config.ENV == 'production':
    base_js = Bundle('js/external/jquery-1.11.1.min.js',
                     'js/external/bootstrap.min.js',
                     'js/external/angular-file-upload-shim.min.js',
                     'js/external/angular.min.js',
                     'js/external/angular-file-upload.min.js',
                     'js/external/angular-resource.min.js',
                     'js/external/angular-sanitize.js',
                     filters='jsmin', output='gen/base.%(version)s.js')
else:
    base_js = Bundle('js/external/jquery-1.11.1.min.js',
                     'js/external/bootstrap.min.js',
                     'js/external/angular-file-upload-shim.js',
                     'js/external/angular.js',
                     'js/external/angular-file-upload.js',
                     'js/external/angular-resource.js',
                     'js/external/angular-sanitize.js',
                     output='gen/base.%(version)s.js')

assets.register('base_js', base_js)
