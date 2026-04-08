/* Hide the "On this page" TOC sidebar on story pages.
 *
 * Adds the class "hide-story-toc" to <body> when the current page lives
 * under one of the story category URL prefixes.  The companion CSS rule in
 * extra.css then hides .md-sidebar--secondary for that body class.
 *
 * Using JS + a body class (instead of CSS :has()) means the hiding works in
 * all browsers, including Firefox versions older than 121.
 */
(function () {
  var storyPrefixes = [
    '/fairy-tales/',
    '/sketches/',
    '/fables/',
    '/fragments/',
    '/myths/',
    '/short-stories/'
  ];
  var path = window.location.pathname;
  for (var i = 0; i < storyPrefixes.length; i++) {
    if (path.indexOf(storyPrefixes[i]) !== -1) {
      document.body.classList.add('hide-story-toc');
      break;
    }
  }
})();
