/*
 * -*- mamba-file-type: mamba-javascript -*-
 */


$(function () {

    $('.github').tooltip({
        selector: "a[data-toggle=tooltip]"
    });

    $('#contact').submit(function(event) {
        $.ajax(
        {
            url: '/contact/form_request',
            type: 'POST',
            dataType: 'json',
            data: {
                'name': $('#name').val(),
                'email': $('#email').val(),
                'content': $('#content').val()
            },
            success: function(json) {
                $('.success').modal({keyboard: true});
            },
            error: function(json) {
                $('.fail').modal({keyboard: true});
            }
        });
    });

});
