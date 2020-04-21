$(function() {
  var clicks = 0;
  $('button').on('click', function() {
      clicks++;
      var percent = Math.min(Math.round(clicks / 3 * 100), 100);
      $('.percent').width(percent + '%');
      $('.number').text(percent + '%');
  });


    $('.Atlanta').on('click', function() {
        window.location.href = "/view?city=Atlanta";
        });
    $('.Paris').on('click', function() {
        window.location.href = "/view?city=Paris";
        });


    $('.facebook').on('click', function() {
        var w = 580, h = 300,
                left = (screen.width/2)-(w/2),
                top = (screen.height/2)-(h/2);


            if ((screen.width < 480) || (screen.height < 480)) {
                window.open ('http://www.facebook.com/share.php?u=https://github.gatech.edu/smarchienne3/Explorify', '', 'toolbar=no, location=no, directories=no, status=no, menubar=no, scrollbars=no, resizable=no, copyhistory=no, width='+w+', height='+h+', top='+top+', left='+left);
            } else {
                window.open ('http://www.facebook.com/share.php?u=https://github.gatech.edu/smarchienne3/Explorify', '', 'toolbar=no, location=no, directories=no, status=no, menubar=no, scrollbars=no, resizable=no, copyhistory=no, width='+w+', height='+h+', top='+top+', left='+left);
            }
    });

    $('.twitter').on('click', function() {
        var loc = encodeURIComponent('https://github.gatech.edu/smarchienne3/Explorify'),
                title = "Explorify: Find spots for awesome photoshots ",
                w = 580, h = 300,
                left = (screen.width/2)-(w/2),
                top = (screen.height/2)-(h/2);

            window.open('http://twitter.com/share?text=' + title + '&url=' + loc, '', 'height=' + h + ', width=' + w + ', top='+top +', left='+ left +', toolbar=0, location=0, menubar=0, directories=0, scrollbars=0');
    });


});
