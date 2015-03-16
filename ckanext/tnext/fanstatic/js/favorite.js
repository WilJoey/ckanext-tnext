// ckan.module('favorite',function (jQuery, _){
//     return {
//         initialize:function (){
//             consoloe.log("I've been initialized for element: %o", this.el);
            
//         }
//     };
// });

$(document).ready(function (){

    var pickers = $(".dpicker input[type=text]").datepicker({
        format:'yyyy/mm/dd'}
    ).on('changeDate', function (ev){
      if(ev.viewMode=='days') $(this).datepicker('hide');
    });
});
