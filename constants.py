html_head_text = """<!DOCTYPE html>
<html lang="en"><head>
  <meta charset="UTF-8">
  <title>%s</title>
  <link rel="shortcut icon" href="https://%s/favicon.ico">
  <link rel="stylesheet" type="text/css" media="screen" href="style.css">"""

html_head_table_style = '<link rel="stylesheet" href="tablesorter.css" type="text/css" media="print, screen">'

close_head_text = """</head>
<body%s>"""

login_form_validator_text = """<script>
<!--
function validate() {
  var ok=true
  if (document.loginform.user.value=="") {
    ok=false
    alert("Please fill in your username.")
    document.loginform.user.focus()
  }
  if (document.loginform.pass.value=="" && ok) {
    ok=false
    alert("Please fill in your passphrase.")
    document.loginform.pass.focus()
  }
  // If we survived all that, allow the submit to occur
  if (ok==true) {
    return true;
  } else {
    return false;
  }
}
//-->
</script>"""

edit_form_validator_text = """<script>
<!--
function validate() {
  if (document.pressed=="Delete") {
      return confirm( "Are you sure you want to delete this row?" );
  }
  return true;
}
//-->
</script>"""

html_body_prefix_text = """"""

login_form_text = """
<div class="login">
<form class="login" action="index.py" method="post" name="loginform" onSubmit="return validate(this);">
<table style="border-spacing:0; padding:1px; border: none;">
<tr class="login">
    <td style="text-align:right; vertical-align:middle">Username:</td>
    <td><input class="login" type="text" size="14" maxlength="14" name="user" value="%s" autocapitalize="off"></td>
</tr>
<tr class="login">
    <td style="text-align:right;">Passphrase:</td><td><input class="login" type="password" autocomplete="off" size="24" maxlength="30" name="pass" value="">
    <input class="login" type="submit" name="submit" value="login"></td>
</tr>
</table>
</form>
</div>"""


type_map = {'Bank Accts': 'bank',
            'Credit Cards': 'cc',
            'Email Accts': 'email',
            'Identification': 'id',
            'Insurance': 'insur',
            'Memberships': 'membership',
            'Vehicle Info': 'vehicle',
            'Web Logins': 'web'}

# ID, Type, Description, Username, Password, URL, Custom, Timestamp, Notes

edit_form_text_start = """<form action="edit.py" method="post" name="editform" onSubmit="return validate(this);">
<table style="border-spacing:0; padding:1px; border: none;">
<tr style="vertical-align:top;">
    <td style="text-align:right;">Type:</td>
    <td>"""
# <select name="type">
#     <option value="bank">Bank Accts</option>
#     <option value="cc">Credit Cards</option>
#     <option value="email">Email Accts</option>
#     <option value="id">Identification</option>
#     <option value="insur">Insurance</option>
#     <option value="membership">Memberships</option>
#     <option value="vehicle">Vehicle Info</option>
#     <option selected value="web">Web Logins</option>
# </select>
edit_form_text_end = """</td>
</tr>
<tr style="vertical-align:top;">
    <td style="text-align:right;">Description:</td><td><input type="text" size="30" maxlength="40" name="desc" value="%s" autocapitalize="off"></td>
</tr>
<tr style="vertical-align:top;">
    <td style="text-align:right;">Name:</td><td><input type="text" size="30" maxlength="40" name="user" value="%s" autocapitalize="off"></td>
</tr>
<tr style="vertical-align:top;">
    <td style="text-align:right;">Password:</td><td><input type="text" size="30" maxlength="40" name="sess" value="%s" autocapitalize="off">%s</td>
</tr>
<tr style="vertical-align:top;">
    <td style="text-align:right;">URL:</td><td><input type="text" size="60" maxlength="800" name="url" value="%s" autocapitalize="off"></td>
</tr>
<tr style="vertical-align:top;">
    <td style="text-align:right;">Custom:</td><td><input type="text" size="60" maxlength="200" name="custom" value="%s" autocapitalize="off"></td>
</tr>
<tr style="vertical-align:top;">
    <td style="text-align:right;">Notes:</td><td><textarea rows="4" cols="40" maxlength="800" title="notes" name="notes">%s</textarea>%s</td>
</tr>
<tr>
    <td colspan="2" style="text-align:right;"><input type="submit" name="submit" onclick="document.pressed=this.value" value="OK"> <input type="submit" name="submit" onclick="document.pressed=this.value" value="Cancel">%s</td>
</tr>
</table>
</form>"""

table_sorter_headers_text = """  <script src="jquery.js"></script>
  <script src="jquery.tablesorter.min.js"></script>
  <script src="jquery.uitablefilter.js"></script>
  <script>

$(document).ready(function(){
  $("#myTable").tablesorter( { sortList: [[1,0], [2,0]],
                               headers: { 0: { sorter: false }, 4: { sorter: false }, 5: { sorter: false }, 6: { sorter: false } }
                             } );
  var theTable = $("#myTable");
  $("#filter").keyup(function() {
    $.uiTableFilter( theTable, this.value );
  })

  // Merely selecting text copies it to the clipboard
  document.addEventListener("selectionchange", () => { document.execCommand("copy"); });

  $('#filter-form').submit(function(){
    theTable.find("tbody > tr:visible > td:eq(1)").mousedown();
    return false;
  }).focus(); //Give focus to input field
 });

  </script>"""

table_header = """<div class="sans"><form id="filter-form" name="filterform">Filter: <input name="filter" id="filter" value="" maxlength="30" size="30" type="text" autocapitalize="off">
&nbsp;&nbsp;| &nbsp;<a href="edit.py?id=new">Create a new row</a>.</form></div>
<table style="border-spacing:1px; padding:0px;" id="myTable" class="tablesorter">
<thead>
<tr>
    <th>Action</th>
    <th>Type</th>
    <th>Description</th>
    <th>Username</th>
    <th>Password</th>
    <th>Custom</th>
    <th>Notes</th>
</tr>
</thead>
<tbody>"""

table_footer = "</tbody>\n</table>"

credits_text = """<div class="credits"><a href="https://david.dlma.com/blog/internet-security">About this site</a>.
<a href="https://medium.com/@dblume/thats-not-my-cookie-98aa23088b78">"That's not my cookie"</a> is a tale of a bugfix.<br>
Thanks to <a href="http://jquery.com/">jQuery</a>,
Christian Bach's <a href="http://tablesorter.com/docs/">tablesorter</a>,
Greg Weber's <a href="http://gregweber.info/projects/uitablefilter">uitablefilter</a>,
<a href="http://www.pycrypto.org/">pycrypto</a> (with <a href="http://eli.thegreenplace.net/2010/06/25/aes-encryption-of-files-in-python-with-pycrypto/">Eli's help</a>),
<a href="http://code.google.com/p/py-bcrypt/">py-bcrypt</a> and Evan Fosmark's
<a href="http://www.evanfosmark.com/2009/01/cross-platform-file-locking-support-in-python/">filelock</a>;
otherwise &copy; 2011-2024, David Blume</div>"""

html_footer_text = """</body></html>"""
