f = open('app/static/admin_dashboard.html', encoding='utf-8')
c = f.read()
f.close()

# Remove all window.xxx = xxx lines at bottom of script
import re
c = re.sub(r'\n// Expose to global scope.*?window\.removeFromHistory = removeFromHistory;\n', '\n', c, flags=re.DOTALL)

# Replace onclick="doAdminLogin()" with id-based approach
c = c.replace('onclick="doAdminLogin()"', 'id="loginBtn2"')

# Add event listener setup at end of script, before </script>
listener_code = """
// Attach all event listeners after DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  var lb = document.getElementById('loginBtn2');
  if (lb) lb.addEventListener('click', doAdminLogin);
  var ap = document.getElementById('adminPass');
  if (ap) ap.addEventListener('keydown', function(e){ if(e.key==='Enter') doAdminLogin(); });
});
"""

c = c.replace('</script>\n</head>', listener_code + '</script>\n</head>')

f = open('app/static/admin_dashboard.html', 'w', encoding='utf-8')
f.write(c)
f.close()
print('Done')
