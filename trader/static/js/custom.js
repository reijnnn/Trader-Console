$(function () {
	$('.navbar-toggle-sidebar').click(function () {
		$('.navbar-nav').toggleClass('slide-in');
		$('.side-body').toggleClass('body-slide-in');
	});

	$('.confirm-delete, .confirm-reset').on('click', function () {
		return confirm('Are you sure?');
	});
});
