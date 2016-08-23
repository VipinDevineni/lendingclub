$(function() {
    var Z = (function() {
        var LANDING_PAGE_SECTION = ['#how-it-works-section',
            '#our-story-section',
            '#plan-overview-section',
            '#misson-statement-section',
            '#faq-section'
        ];

        function createChartOptions(opt) {
            return {
                title: opt.title,
                titleTextStyle: {
                    fontSize: 20,
                    color: '#555',
                },
                hAxis: {
                    title: opt.hAxis.title,
                },
                vAxis: {
                    title: opt.vAxis.title,
                },
                legend: {
                    position: 'right',
                    textStyle: {
                        color: 'blue',
                        fontSize: 12
                    }
                },
                width: 740,
                height: 460,
                series: {
                    0: {
                        lineWidth: 3,
                        color: 'red'
                    },
                    1: {
                        lineWidth: 3,
                        color: 'green'
                    },
                    2: {
                        lineWidth: 3,
                        color: 'red'
                    },
                    3: {
                        lineWidth: 3,
                        color: 'green'
                    }
                },
            };
        }

        function drawChart() {
            var interestData = google.visualization.arrayToDataTable([
                ["Days", "Borrow $150 (Payday)", {
                    role: "style"
                }, {
                    role: 'annotation'
                }, "Borrow $150 (Ziplly)", {
                    role: "style"
                }, {
                    role: 'annotation'
                }],
                [0, 30, "#f44336", undefined, 0, "#4caf50", undefined],
                [14, 30, "#f44336", "$30", 0, "#4caf50", "$0"],
                [28, 60, "#f44336", "$60", 0, "#4caf50", "$0"],
                [42, 90, "#f44336", "$90", 15, "#4caf50", "$15"],
                [56, 120, "#f44336", "$120", 30, "#4caf50", "$30"],
            ]);

            var principalData = google.visualization.arrayToDataTable([
                ["Days", "Borrow $150 (Payday)", {
                    role: "style"
                }, {
                    role: 'annotation'
                }, "Borrow $150 (Ziplly)", {
                    role: "style"
                }, {
                    role: 'annotation'
                }],
                [0, 180, "#f44336", undefined, 150, "#4caf50", undefined],
                [14, 180, "#f44336", "$180", 150, "#4caf50", "$150"],
                [28, 210, "#f44336", "$210", 150, "#4caf50", "$150"],
                [42, 240, "#f44336", "$240", 165, "#4caf50", "$165"],
                [56, 270, "#f44336", "$270", 180, "#4caf50", "$180"],
            ]);

            // Instantiate and draw our chart, passing in some options.
            var chart = new google.visualization.LineChart(document.getElementById('interest-comparison'));
            chart.draw(interestData, createChartOptions({
                'title': 'Interest charge comparison: Payday vs Ziplly',
                'hAxis': {
                    'title': 'Days'
                },
                'vAxis': {
                    'title': 'Interest charge($)'
                }
            }));

            var chart = new google.visualization.LineChart(document.getElementById('principal-comparison'));
            chart.draw(principalData, createChartOptions({
                'title': 'Amount owed comparison: Payday vs Ziplly',
                'hAxis': {
                    'title': 'Days'
                },
                'vAxis': {
                    'title': 'Amount owed ($)'
                }
            }));
        }

        function registerChartHandler() {
            drawChart();
        }

        function register_user() {
            var emailRegex = /\S+@\S+\.\S+/
            var email = $("input[name='email']").val();
            if (email == undefined || email.length == 0) {
                Materialize.toast('Must enter email address', 3000);
                return;
            }

            if (!emailRegex.test(email)) {
                Materialize.toast('Must enter email address', 3000);
                return;
            }

            var toast_duration = 3000;
            $.post(
                '/register_user_ajax', {
                    'email': email,
                },
                function(data) {
                    var content = "<div>";
                    if (data.error) {
                        Materialize.toast('Failed to register user: ' + email, toast_duration);
                    } else {
                        Materialize.toast('Thanks for registering', toast_duration);
                    }
                    $("input[name='email']").val("");
                }
            )
        }

        $("#notify-btn").click(function(e) {
            e.preventDefault();
            ga('send', {
                'hitType': 'event',
                'eventCategory': 'landing_page',
                'eventAction': 'button_click',
                'eventaLabel': 'notify_button'
            });
            register_user();
        });

        // $('.carousel.carousel-slider').carousel({
        //     full_width: true
        // });
        //
        // function slide() {
        //     $('.carousel').carousel('next');
        //     setTimeout(slide, 4000);
        // }

        function init() {
            google.charts.load('current', {'packages': ['corechart']});
            google.charts.setOnLoadCallback(registerChartHandler);

            (function(i, s, o, g, r, a, m) {
                i['GoogleAnalyticsObject'] = r;
                i[r] = i[r] || function() {
                    (i[r].q = i[r].q || []).push(arguments)
                }, i[r].l = 1 * new Date();
                a = s.createElement(o),
                    m = s.getElementsByTagName(o)[0];
                a.async = 1;
                a.src = g;
                m.parentNode.insertBefore(a, m)
            })(window, document, 'script', 'https://www.google-analytics.com/analytics.js', 'ga');

            ga('create', 'UA-82892733-1', 'auto');
            ga('send', 'pageview');
            // slide();

            $(window).scroll(function() {
                // console.log('scrolling wTop = '+$(window).scrollTop());
                for (var i = LANDING_PAGE_SECTION.length - 1; i >= 0; i--) {
                    var sectionTop = $(LANDING_PAGE_SECTION[i]).position().top;
                    if ($(window).scrollTop() >= sectionTop) {
                        ga('send', {
                            'hitType': 'event',
                            'eventCategory': 'scroll',
                            'eventAction': 'view',
                            'eventaLabel': LANDING_PAGE_SECTION[i].substring(1)
                        });
                        break;
                    }
                }
            });
        }
        return {
            init: init
        };
    }());

    Z.init();
});
