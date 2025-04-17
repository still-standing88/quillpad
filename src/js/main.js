
import 'bootstrap/dist/css/bootstrap.min.css';
import '@toast-ui/editor/dist/toastui-editor.css';
import '../css/style.css';

import $ from 'jquery';
import 'bootstrap';
import Editor from '@toast-ui/editor';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

window.$ = $;
window.jQuery = $;
window.marked = marked;
window.DOMPurify = DOMPurify;
window.toastui = { Editor: Editor };

import * as api from './core/api.js';
import * as auth from './core/auth.js';
import * as uiCommon from './ui/common.js';
import * as uiNavbar from './ui/navbar.js';
import * as uiPosts from './ui/posts.js';
import * as uiComments from './ui/comments.js';
import * as uiForms from './ui/forms.js';
import * as uiProfile from './ui/profile.js';
import * as uiAdmin from './ui/admin.js';
import * as profileHandlers from './handlers/profileHandlers.js';
import * as postHandlers from './handlers/postHandlers.js';
import * as commentHandlers from './handlers/commentHandlers.js';
import * as adminHandlers from './handlers/adminHandlers.js';
import * as router from './router.js';
import { initialize } from './core/init.js';

window.api = api;
window.auth = auth;
window.ui = { common: uiCommon, navbar: uiNavbar, posts: uiPosts, comments: uiComments, forms: uiForms, profile: uiProfile, admin: uiAdmin };
window.handlers = { profile: profileHandlers, posts: postHandlers, comments: commentHandlers, admin: adminHandlers };
window.router = router;

$(document).ready(() => { initialize(); });
