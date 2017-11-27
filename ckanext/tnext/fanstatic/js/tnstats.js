var config = { };
$(document).ready(function (){
    var checkName = '',
        rowCount = 1,
        checkTd = null;

    $('.table tr').each(function(i, d) {
        if (i == 0) return;
        var td = $(d).children().first();
        if (td.html() != checkName) {
            checkName = td.html();
            if (checkTd) {
                checkTd.attr("rowspan", rowCount);
            }
            rowCount = 1;
            checkTd = td;
        } else {
            td.remove();
            rowCount++;
        }
    });
    
    checkTd.attr("rowspan", rowCount);
    config = getConfig($('#hidConfig').val());

    $('#btnDownload').click(function (){
        window.open(config.windowOpenUrl);
    });

});

function getConfig(val){
    if(val === 'org'){
        return {
            menuIndex: 0,
            selectId:'#selOrg',
            title: 'org_name',
            dataUrl: '/tnstats/orgApi',
            windowOpenUrl :'/tnstats/orgCsv'
        }
    }else{
        return {
            menuIndex: 1,
            selectId:'#selGroup',
            title: 'group_name',
            dataUrl: '/tnstats/groupApi',
            windowOpenUrl :'/tnstats/groupCsv'
        }
    }
}
