function CalibrationManagement () {
    this.start_calibration = function(event) {
        var self_obj = event.data.ths;
        $.ajax({ type:"POST",
            url:"/glove/startCalibration/",
            complete : self_obj.complete_handler
        });

        $("#stop_calibration").button( "enable");
        return false;
    };

    this.stop_calibration = function(event) {
        var self_obj = event.data.ths;
        $.ajax({ type:"POST",
            url:"/glove/stopCalibration/",
            complete : self_obj.complete_handler
        });
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
}

