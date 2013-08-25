function NetworkManagement () {
	this.image_index = 0;
	this.max_image_index = 4;
	
	this.curent_index = 0;
	this.snapshot_num = 4;

    this.alphabet= ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r",
        "s", "t", "u", "v", "w", "x", "y"];

    $(".message").click(function() {
        $(".info_message").removeClass( "top65" );
    });

    this.trainTheNetwork = function(event) {
    	var self_obj = event.data.ths;
	    $.ajax({ type:"POST", 
	    	url:"/glove/train/",
			complete : self_obj.train_complete_handler
		});
	    return false;
	};
	
	this.testTheNetwork = function(event) {
		var self_obj = event.data.ths;
		$.ajax({
			type : "POST",
			url : "/glove/testData/",
			complete : self_obj.complete_handler
		});
		return false;
	};
	
	this.take_snapshot = function(event) {
        $("#ready").button("disable");
		var self_obj = event.data.ths;
		self_obj.curent_index ++;
		// --------- send request------
		var data_for_test = (self_obj.curent_index > 2) ? 1 : 0;
		var data = {
			class_data : self_obj.alphabet[self_obj.image_index],
			for_test : data_for_test
		};
		var args = {
			type : "POST",
			url : "/glove/add/",
			data : data,
            dataType: "json",
			complete : function(jqXHR, textStatus){
                self_obj.add_data_complete_handler(self_obj, jqXHR, textStatus)
            }

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
            setNextIcon(self_obj);
		}
		
		return false;
	};

    this.add_data_complete_handler = function(self_obj, res, status) {
        $("#ready").button( "enable");
        this.complete_handler(res, status);
    };


	this.complete_handler = function(res, status) {
	    if (status == "success") {
	    	var data = $.parseJSON(res.responseText);
	    	if(data.status == 0){
	    		$(".message").message({type:"error", message: data.message});
	    		$(".message").show();
                $(".info_message").addClass( "top65" );
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


    this.begin_to_recognize = function(event) {
        var self_obj = event.data.ths;
        $.ajax({ type:"POST",
            url:"/glove/doRecognize/",
            complete : self_obj.show_result_of_recognition
        });
        return false;
    };


    this.show_result_of_recognition = function(res, status, event) {
//        var data = $.parseJSON(res.responseText);
        if (status == "success") {
//    	    	alert(res.responseText["message"]);
            if(res.responseText.indexOf("Empty") == -1){
                $("#recognized").text( res.responseText);
                var fullMessage = res.responseText;
                var newLetter = fullMessage.substring(fullMessage.indexOf("message")+"message".length+3).replace(/\"/g, "").replace("}", "")

                var oldVal = $("#fullRecognized").text();
                var oldLastLetter = oldVal.substring(oldVal.length-1);
                if(newLetter != "Unknown" && newLetter != "Empty" && newLetter != oldLastLetter){
                    $("#fullRecognized").text(oldVal + newLetter);
                }
            }

            $("#start_recognize").click();
        }
        else
        {
            $(".message").message({type:"error", message:res.responseText});
            $("#start_recognize").click();
        }
    }

    this.clearOldTrainingData = function(event) {
        var self_obj = event.data.ths;
        $.ajax({ type:"POST",
            url:"/glove/doClearOldTrainingData/",
            complete : self_obj.complete_handler
        });
        return false;
    };

    function setNextIcon(self_obj) {
        var image_src = "/static/images/set/" + self_obj.alphabet[self_obj.image_index] + ".jpg";
        $('#training_icon').attr('src', image_src).load(function () {
            this.width;   // Note: $(this).width() will not work for in memory images

        });
    }

    this.skip = function(event) {
        var self_obj = event.data.ths;
        ++self_obj.image_index;
        setNextIcon(self_obj);
        return false;
    };


    this.add_sign = function(event) {
        var self_obj = event.data.ths;
        $('#trainingArea').css("display", "none");
        $('#addingArea').css("display", "block")
    }

    this.fetch_all_signs = function(){
        var alphabetIcons = []

        for(index in this.alphabet){
            alphabetIcons.push(this.alphabet[index] + ".jpg");
        }

        var allSigns = $.merge(alphabetIcons, customFiles);

        var div = document.getElementById("allSigns");
        var i = 0;

        while(i < allSigns.length){

            var newDiv = document.createElement('div');
            newDiv.setAttribute("class", "signDiv");
            var newImage = document.createElement("img");

            var imageBase = i < this.alphabet.length ? "/static/images/set/" : "/static/images/" +userId +"/set/"
            var image_src = imageBase + allSigns[i];
            newImage.src = image_src;
            newImage.setAttribute("class", "signImage");
            newDiv.appendChild(newImage);

            var label = document.createElement('label');

            var symbol = allSigns[i].substr(0, allSigns[i].lastIndexOf("."));
            var symbolRateClass = userClassInfo.get(symbol);
            label.innerHTML= symbol;
            label.setAttribute("class", "bottomLabel");
            newDiv.appendChild(label);
            $(newDiv).addClass(symbolRateClass);
            div.appendChild(newDiv);

            i++;
        }

    }

    this.add_sign_complete_handler  = function(res, status) {
        //TODO bind to this and call to complete_handler
        if (status == "success") {
            var data = $.parseJSON(res.responseText);
            if(data.status == 0){
                $(".message").message({type:"error", message: data.message});
                $(".message").show();
            }else{
                var fld = document.getElementById("upload_file");
                fld.form.reset();
                $('#trainingArea').css("display", "block");
                $('#addingArea').css("display", "none")
            }
        }
        else
        {
            $(".message").message({type:"error", message: res.responseText});
        }

    };
}

