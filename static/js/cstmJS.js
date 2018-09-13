$(document).ready(function(){
	var bodyHeight = $("body").height();
	var btmNavHeight = $(".bottomNav").height();
	var btmNavBodyHeight = bodyHeight - btmNavHeight - footerHeight - 40;
	var sideNavBodyHeight = bodyHeight - footerHeight + 5;
	//$("#page-wrapper").css("height",btmNavBodyHeight).css("min-height","inherit").css("overflow","auto");
	$(".btmNavBody").css("height",btmNavBodyHeight);
	$(".sideNavBody").css("height",sideNavBodyHeight);

	var footerHeight = $(".footer").height();  //+ 9
	$(".bottomNav").css("bottom",footerHeight);


	$(".sidebar-click").click(function(){
        //alert(thik hai...);
        //location.href = $(this).attr('data-info');
//        job_id = $("#job_id")[0].value;
        disease = $("#case_disease_name").val()
        if (disease && disease.length > 0){
            $("#next_url").val($(this).attr('data-info'));
            $("#saveInfo").modal('show');
        }
        else{
            location.href = $(this).attr('data-info');
        }
    });


});



$('#cancelJob').on('click', function() {
	location.href = $("#next_url").val();
});



//Minimalize menu
$('.navbar-minimalize').on('click', function () {
	$(".navbar-static-side").toggleClass("bottomNav").toggleClass("sideNav");
	SmoothlyMenu();
	$("#page-wrapper").toggleClass("btmNavBody").toggleClass("sideNavBody");
});


$("#side-menu li").click(function(){
    $("#side-menu li").removeClass("active");
    $(this).addClass("active");
})









