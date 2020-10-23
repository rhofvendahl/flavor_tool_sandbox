$(document).ready(function() {
    var stirFryManager = new StirFryManager();
    stirFryManager.load();
    gtag('event', 'page_load', {
        'event_category': 'page',
        'event_label': 'Load Page,
        'non_interaction': true,
    });

});
