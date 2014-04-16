"""
Galaxy Trello card creator

POST /1/cards
Required permissions: write

Arguments
name (required)
    Valid Values: a string with a length from 1 to 16384
desc (optional)
    Valid Values: A user ID or name
idList (required)
    Valid Values: id of the list that the card should be added to

POST /1/cards/[card id or shortlink]/actions/comments
Required permissions: comments
Arguments
text (required)
Valid Values: a string with a length from 1 to 16384

"""
import bottle
import json
import os
import urllib
import urllib2

trello_url = "https://api.trello.com/1/cards"

trello_auth_key = os.environ.get('TRELLO_AUTH_KEY')
trello_oauth_token = os.environ.get('TRELLO_OAUTH_TOKEN')

# Identifier of the "Galaxy Inbox" trello list.
input_list_id = '511170b2f10a1bfa7300bc77'


PAGE = '''
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML//EN"> <html><head><title>The Galaxy Project: Online bioinformatics analysis for
everyone</title> <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"> <link href="static/gxystyle.css"
media="screen" rel="Stylesheet" type="text/css">
<style type="text/css">
</style>

<script type="text/javascript" src="static/jquery.js"></script>
<script type="text/javascript" src="static/jquery.form.js"></script>
<script type="text/javascript">
$(document).ready(function(){
    $('form').ajaxForm({
        type: 'POST',
        dataType: 'json',
        success: function(data){
            $('#id_name').val("");
            $('#id_desc').val("");
            $('#response_container').append('<div>You have successfully created the card <a href="'+data.url+'"><b>'+data.name+'</b></a><hr/></div>');
            }
        });
});
</script>

</head> <body> <div id="everything"> <div id="masthead"> <div
id="masthead-inner"> <div class="title"> <a href="http://usegalaxy.org/"><img src="static/galaxyIcon_noText.png"
style="width: 26px; vertical-align: top;" border="0"> Galaxy</a> </div> </div> </div> <div id="content">

<div><p class="opening_text">
<img class="fi_right" src="static/trello.png"/>
Galaxy uses uses Trello for issue tracking and development planning.  Trello is
a simple online kanban board that provides a comprehensive view of what's being
worked on and what the progress is of particular development efforts.<br/> If
you have an idea for an improvement, or would like to report a bug, please do
fill out the form below.  Before you do so, however, please check the board to
ensure that the issue you're reporting doesn't already have an active Trello
card.  We'd love for everyone to also vote for issues that are important to
them.  The board is automatically sorted by several heuristics hourly in order
to make the most important issues (as determined by votes, commentary, etc.)
bubble to the top of each list.</p>

<p class="opening_text"> <a
href="https://trello.com/b/75c1kASa/galaxy-development">Visit the Trello
board</a> to review, comment on, and vote for currently open issues.  To create
a new issue, simply fill out the form below and a card will be created in the
"Development Inbox" list of the board.  If you fill out the "Your Trello
Username" field, you'll be @mentioned on the card in a comment, and should be subscribed to
future updates.</p></div>
<div id="interaction_container">
    <div id="response_container">
    </div>
    <div id="form_container">
        <form method="POST" action="/trello">
          <label for="id_name">Card Name</label><input id="id_name" name="name" size="80" type="text" placeholder="Please be descriptive"/><br/>
          <label for="id_submitter">Your Trello Username</label><input id="id_submitter" name="submitter" size="80" type="text" placeholder="@dannon"/><br/>
          <label for="id_desc">Description</label><textarea rows="8" cols="60" id="id_desc" name="desc" type="text" placeholder="Detailed description of the issue or feature request.  If it's a bug, please include exact steps to reproduce it."></textarea><br/>
          <input type="submit"/>
        </form>
    </div>
</div>

</div> </div></body></html>
'''


@bottle.route('/static/<path:path>')
def callback(path):
        return bottle.static_file(path, root='static/')


@bottle.get('/')
def create_form():
    return PAGE


@bottle.post('/')
def create_submit():
    name = bottle.request.forms.get('name')
    desc = bottle.request.forms.get('desc')
    submitter = bottle.request.forms.get('submitter')
    return _create_card(name, desc, submitter)


def _create_card(name, desc, submitter):
    #First create the card
    create_data = urllib.urlencode({'name': name,
                                   'idList': input_list_id,
                                   'desc': desc,
                                   'key': trello_auth_key,
                                   'token': trello_oauth_token})
    create_req = urllib2.Request(trello_url + "?key=%s&token=%s" % (trello_auth_key, trello_oauth_token), create_data)
    create_response = urllib2.urlopen(create_req).read()
    create_response_dict = json.loads(create_response)
    # If submitter was specified, add @mention comment.
    if submitter and 'id' in create_response_dict:
        submitter = submitter.strip('@')
        comment_data = urllib.urlencode({'text': "Submitted by @%s" % submitter,
                                        'key': trello_auth_key,
                                        'token': trello_oauth_token})
        comment_req = urllib2.Request(trello_url + "/%s/actions/comments?key=%s&token=%s" % (create_response_dict['id'], trello_auth_key, trello_oauth_token), comment_data)
        json.loads(urllib2.urlopen(comment_req).read())
    return create_response

if __name__ == "__main__":
    bottle.run(host='0.0.0.0', port=8089, reloader=True)
else:
    application = bottle.default_app()
