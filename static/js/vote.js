$(document).ready(function(){
	$('.span-holder').click(function(){
		$('.glyph-rotate').toggleClass('glyph-trans');
		$('.the-post-form').toggleClass('active');
		if($('.the-post-form').hasClass('active')){
			setTimeout(function(){
				$('.the-post-form').css({'visibility': 'visible'})
			},200);	
		}else{
			setTimeout(function(){
			$('.the-post-form').css({'visibility': 'hidden'})
			}, 10);
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
			url: "/process_vote",
			type: "post",
			data: {vid:vid, voteType:voteType},
			success: function(result){
				if(result.message == 'voteChanged'){
					//the user's vote was updated by python. update our field in html
					$("p[up-down-id='" + vid + "']").html(result.vote_total)
					console.log(result.vote_total)
				}else if(result.message == 'alreadyVoted'){
					// #user already voted. let them know
					$("p[up-down-id='" + vid + "']").html('you have already voted on this bawk!')
				}else if(result.message == 'voteCounted'){
					$("p[up-down-id='" + vid + "']").html(result.vote_total)
				}
				console.log(result)
			}
		});
	});
});