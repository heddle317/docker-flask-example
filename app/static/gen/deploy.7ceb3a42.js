angularApp.controller('BuildController', ['$scope', '$http', '$window', '$log', '$timeout', function($scope, $http, $window, $log, $timeout) {
    $scope.currentDeploy = null;
    $scope.builds = [];
    $scope.building = null;
    $scope.loading = true;
    $scope.endBuilds = false;
    $scope.getMoreBuilds = function() {
        var lastBuild = $scope.builds[$scope.builds.length - 1];
        $scope.getBuilds(lastBuild.uuid, false);
        $scope.loading = true;
    };
    $scope.getBuilds = function(lastBuild, poll) {
        var data = {'last_build': lastBuild};
        $http.get('/api/services/' + $scope.serviceName + "/builds", {params: data}).success(function (response) {
            $scope.loading = false;
            if (response.builds.length < 4) {
                $scope.endBuilds = true;
            }
            for (var i = 0; i < response.builds.length; i++) {
                $scope.updateBuild(response.builds[i]);
            }
            $scope.building = response.building;
            if (poll) {
                $timeout(function() {
                    $scope.getBuilds(null, true);
                }, 30000);
            }
        });
    };
    $scope.getBuilds(null, true);
    $scope.currentlyRunning = function(build) {
        var i;
        for (i = 0; i < build.deploys.length; i++) {
            if (build.deploys[i].currently_running) {
                return true;
            }
        }
        return false;
    };
    $scope.currentlyDeployingLogs = function(build) {
        var i;
        var deploy;
        for (i = 0; i < build.deploys.length; i++) {
            deploy = build.deploys[i];
            if (deploy.started && !deploy.finished) {
                return deploy.logs;
            }
        }
    };
    $scope.currentlyDeploying = function(build) {
        var i;
        var deploy;
        for (i = 0; i < build.deploys.length; i++) {
            deploy = build.deploys[i];
            if (deploy.started && !deploy.finished) {
                return true;
            }
        }
        return false;
    };
    $scope.deploysFinished = function(build) {
        var i;
        var deploy;
        for (i = 0; i < build.deploys.length; i++) {
            deploy = build.deploys[i];
            if (!deploy.finished) {
                return false;
            }
        }
        return true;
    };
    $scope.shortenHash = function(hash) {
        return hash.substring(0, 7);
    };
    $scope.shortenMessage = function(message) {
        if (message.length > 100) {
            return message.substring(0, 100) + '...';
        }
        return message;
    };
    $scope.pollBuild = function(build) {
        $http.get('/api/services/' + build.service_uuid + "/builds/" + build.uuid).success(function(response) {
            $scope.updateBuild(response);
            if ($scope.deploysFinished(response)) {
                return;
            }
            $timeout(function() {
                $scope.pollBuild(response);
            }, 2000);
        });
    };
    $scope.updateBuild = function(build) {
        if ($scope.builds.length > 0) {
            var firstBuild = $scope.builds[0];
            if (build.created_at > firstBuild.created_at) {
                $scope.builds.unshift(build);
                return;
            }
        }
        var i;
        for (i = 0; i < $scope.builds.length; i++) {
            if (build.uuid === $scope.builds[i].uuid) {
                $scope.builds[i] = build;
                return;
            }
        }
        $scope.builds.push(build);
    };
    $scope.markFinished = function(build) {
        $http.post('/api/services/' + build.service_uuid + "/builds/" + build.uuid, data={'finished': true}).success(function(response) {
            $scope.updateBuild(response);
        });
    };
    $scope.deployLatestBuild = function(build) {
        $http.post('/api/services/' + build.service_uuid + "/builds/" + build.uuid + '/deploy').success(function(response) {
            $scope.updateBuild(response);
            $timeout(function() {
                $scope.pollBuild(response);
            }, 5000);
        });
    };
    $scope.markFailed = function(build, deploy) {
        $http.post('/api/services/' + build.service_uuid + "/deploy/" + deploy.uuid, data={'finished': true, 'failed': true}).success(function(response) {
            $scope.updateBuild(response);
        });
    };
    $scope.deployContainer = function(deploy) {
        var $btn = $('.' + deploy.uuid + ' .btn.deploy').button('loading');
        $http.post('/api/services/' + deploy.service_uuid + '/deploy/' + deploy.uuid + '/restart').success(function(response) {
            $scope.updateBuild(response);
            $btn.button('reset');
            $timeout(function() {
                $scope.pollBuild(response);
            }, 2000);
        });
    };
    $scope.deleteContainer = function(deploy) {
        var confirm = $window.confirm("Are you sure you want to delete this container?");
        if (!confirm) {
            return;
        }
        var $btn = $('.' + deploy.uuid + ' .btn.delete').button('loading');
        $http.delete('/api/services/' + deploy.service_uuid + '/deploy/' + deploy.uuid).success(function(response) {
            $scope.updateBuild(response);
            $btn.button('reset');
        });
    };
}]);
