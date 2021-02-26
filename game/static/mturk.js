$(document).ready(function() {
    // Instructions expand/collapse
    var content1 = $('#descriptionBody');
    var content2 = $('#informationBody');
    var trigger1 = $('#descriptionTrigger');
    var trigger2 = $('#informationTrigger');
    content1.hide();
    content2.hide();
    $('.collapse-text').text('(Click to expand)');
    trigger1.click(function(){
      content1.toggle();
      var isVisible = content1.is(':visible');
      if(isVisible){
        $('.collapse-text').text('(Click to collapse)');
      }else{
        $('.collapse-text').text('(Click to expand)');
      }
    });
    trigger2.click(function(){
      content2.toggle();
      var isVisible = content2.is(':visible');
      if(isVisible){
        $('.collapse-text').text('(Click to collapse)');
      }else{
        $('.collapse-text').text('(Click to expand)');
      }
    });
});

