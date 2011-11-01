var voteDialog;
var sorryDialog;

var vote = function(result, dialog) {
    var id = $('#id').val()
    $.ajax({
        type: 'POST',
        data: {'id': id, 'result': result},
        async: false,
        complete: function(XMLHttpRequest, textStatus) {
            dialog.dialog('close');
        },
    });
}

var redirect_top = function() {
    location.href = '/';
}

$(function() {
    voteDialog = $('#votedialog').dialog({
        autoOpen: false,
        modal: true,
        title: 'Well, do you feel sexy?',
        buttons: {
            'Yes, well!': function() { vote('yes', $(this)); },
            'No, sorry...': function() { vote('no', $(this)); }
        },
        close: function(event, ui) { redirect_top(); }
    });
    
    sorryDialog = $('#sorrydialog').dialog({
        autoOpen: false,
        modal: true,
        title: 'Sorry...',
        buttons: {
            'OK': function() { $(this).dialog('close'); },
        },
        close: function(event, ui) { redirect_top(); }
    });

    var id = $("#id").val();
    var audio = new Audio('/proxy/' + id);
    audio.addEventListener('ended', function(e) {
        voteDialog.dialog('open');
    }, false);
    audio.addEventListener('error', function(e) {
        soryyDialog.dialog('open');
    }, false);
    audio.play();
});
