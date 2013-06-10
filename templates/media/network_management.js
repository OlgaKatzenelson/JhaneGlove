function NetworkManagement () {
	this.image_index = 0;
	this.max_image_index = 4;
	
	this.curent_index = 0;
	this.snapshot_num = 4;
    
    this.trainTheNetwork = function(event) {
    	var self_obj = event.data.ths;
	    $.ajax({ type:"POST", 
	    	url:"/glow/train/", 
			complete : self_obj.train_complete_handler
		});
	    return false;
	};
	
	this.testTheNetwork = function(event) {
		var self_obj = event.data.ths;
		$.ajax({
			type : "POST",
			url : "/glow/testData/", 
			complete : self_obj.complete_handler
		});
		return false;
	};
	
	this.take_snapshot = function(event) {
		var self_obj = event.data.ths;
		self_obj.curent_index ++;
		// --------- send request------
		var data_for_test = (self_obj.curent_index > 2) ? 1 : 0;
		var data = {
			class_id : self_obj.image_index,
			for_test : data_for_test
		};
		var args = {
			type : "POST",
			url : "/glow/add/",
			data : data, 
			complete : self_obj.complete_handler
		};
		$.ajax(args);
		
		
		
		
		//display same image 'snapshot_num' times
		if(self_obj.curent_index < self_obj.snapshot_num){
			return false;
		}else{
			//-----------change icon ----------
			self_obj.image_index ++;
			self_obj.curent_index = 0;
		}
		
		if(self_obj.image_index > self_obj.max_image_index){
			//start trainning
			$("#ready").hide();
			$('#training_icon').hide();
			$('#explanations').hide();
			$("#exec_train").button( "enable");
			
			$(".message").message("hide");; //hide the errors
			
			var user_message = "You finished with addition of information and are ready for training the system.   ";
			$(".info_message").message('options',{ message: user_message});
			$(".info_message").message("show");
			$("#step").text( "Step : Training");
		}else{
			var image_src = "/static/images/set/"+ self_obj.image_index + ".jpg";
			$('#training_icon').attr('src', image_src).load(function(){
			    this.width;   // Note: $(this).width() will not work for in memory images

			});
		}
		
		return false;
	};
	
	
	this.complete_handler = function(res, status) {
	    if (status == "success") {
	    	var data = $.parseJSON(res.responseText);
	    	if(data.status == 0){
	    		$(".message").message({type:"error", message: data.message});
	    		$(".message").show();
	    	}else if(data.message != ""){
	    		$(".info_message").message({type:"info", message: data.message}); //for first displaying
	    		$(".info_message").message('options',{ message: data.message}); //for text replace
				$(".info_message").message("show");
	    	}
	    }
	    else
	    {
	        $(".message").message({type:"error", message: res.responseText});
	    }
	};
	
	this.train_complete_handler = function(res, status) {
	    if (status == "success") {
	    	var data = $.parseJSON(res.responseText);
	    	if(data.status == 0){
	    		$(".message").message({type:"error", message: data.message});
	    		$(".message").show();
	    	}else if(data.message != ""){
	    		$(".info_message").message('options',{ message: data.message}); //for text replace
				$(".info_message").message("show");
				$("#do_test").button( "enable");
				$("#step").text( "Step : Testing");
	    	}
	    }
	    else
	    {
	        $(".message").message({type:"error", message: res.responseText});
	    }
	};
}

