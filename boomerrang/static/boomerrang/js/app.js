'use strict';

$(function() {
    // Remove all non-American timezones
    $('#id_timezone').val('America/Los_Angeles');
    $('#id_timezone option').each(function() {
        if (!$(this).val().startsWith('America')) {
            $(this).remove();
        }
    });

    $('form#contactForm').submit(function() {
        var timeZone = $('#id_timezone').val();
        var timeStamp = $('#id_time_scheduled').val();
        var tzAwareTime = moment(timeStamp).tz(timeZone);
        // toISOString always converts time to 0-offset (UTC)
        $('#id_time_scheduled_utc').val(tzAwareTime.toISOString());

        return true;
    });
});
