$(document).ready(function(){
	$('.span-holder').click(function(){
		$('.glyph-rotate').toggleClass('glyph-trans');
		$('.the-post-form').toggleClass('active');
		if($('.the-post-form').css('visibility') == 'hidden'){
			setTimeout(function(){
				$('.the-post-form').css({'visibility': 'visible', 'height': 'auto'})
			},10);	
		}else{
			setTimeout(function(){
			$('.the-post-form').css({'visibility': 'hidden', 'height': '0px'})
			}, 200);
		}
	})

	$('.vote').click(function(){
		var vid = $(this).attr('post_id')
		if($(this).hasClass("upvote")){
			// user voted on the up arrow
			var voteType = 1;
		}else{
			// user must have voted on the down arrow. Vote down
			var voteType = -1;
		}
		$.ajax({
			url: "process_vote",
			type: "post",
			data: {vid:vid, voteType:voteType},
			success: function(result){
				console.log(result)
			}
		})
	});
});