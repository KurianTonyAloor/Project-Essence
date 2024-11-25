$(document).ready(function() {
    // Create new user
    $('#createUser').on('click', function() {
        $.ajax({
            type: 'POST',
            url: '/create_user',
            success: function(response) {
                $('#userResult').text(response.message);
            },
            error: function() {
                $('#userResult').text("Error creating user.");
            }
        });
    });

    // Load existing user
    $('#loadUser').on('click', function() {
        const userId = $('#userIdInput').val();
        $.ajax({
            type: 'POST',
            url: '/load_user',
            contentType: 'application/json',
            data: JSON.stringify({user_id: userId}),
            success: function(response) {
                $('#userResult').text(response.message);
            },
            error: function(response) {
                $('#userResult').text(response.responseJSON.error || "Error loading user.");
            }
        });
    });

    // Add detail
    $('#detailForm').on('submit', function(e) {
        e.preventDefault();

        const detail = $('#userInput').val();
        const topics = $('#topicsInput').val().split(',');
        const time = $('#timeInput').val();

        $.ajax({
            type: 'POST',
            url: '/add_detail',
            contentType: 'application/json',
            data: JSON.stringify({
                detail: detail,
                topics: topics,
                time: time
            }),
            success: function(response) {
                $('#detailResult').text(response.message);
            },
            error: function() {
                $('#detailResult').text("Error adding detail.");
            }
        });
    });

    // Predict next action at a specific time
    $('#predictionTimeForm').on('submit', function(e) {
        e.preventDefault();

        const inputTime = $('#timePredictInput').val();

        $.ajax({
            type: 'POST',
            url: '/predict_next_action_at_time',
            contentType: 'application/json',
            data: JSON.stringify({
                time: inputTime
            }),
            success: function(response) {
                $('#predictionTimeResult').text(response.prediction || "No prediction available.");
            },
            error: function() {
                $('#predictionTimeResult').text("Error predicting next action.");
            }
        });
    });

    // Generate insights
    $('#generateInsights').on('click', function() {
        $.ajax({
            type: 'GET',
            url: '/generate_insights',
            success: function(response) {
                $('#insightsResult').text(JSON.stringify(response));
            },
            error: function() {
                $('#insightsResult').text("Error generating insights.");
            }
        });
    });
});
