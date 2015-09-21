angularApp.controller('UsermgmtController', ['$scope', '$http', '$window', '$log', function($scope, $http, $window, $log) {
    $scope.users = [];
    $scope.currentUser = null;
    $scope.newUserEmail = '';
    $http.get('/api/users').success(function(response) {
        $scope.users = response;
    });
    $scope.sendInvite = function(email, user_uuid) {
        if (user_uuid != '') {
            var $btn = $('.' + user_uuid + ' .btn.invite').button('loading');
        } else {
            var $btn = $('.btn.invite-user').button('loading');
        }
        var index = $scope.getIndex(user_uuid);
        $http.post('/api/users/invite', data={'email':email}).success(function(response) {
            $scope.updateUserList(index, response);
            if (user_uuid != '') {
                $('.' + user_uuid + ' .fa-check').show('fast').delay(3000).fadeOut(300);
            } else {
                $('#inviteUserModal').modal('hide');
                $scope.newUserEmail = '';
            }
        }).finally(function() {
            $btn.button('reset');
        });
    };
    $scope.updateUser = function(user) {
        $scope.currentUser = user;
    };
    $scope.undelete = function(user) {
        user.dead = false;
        var $btn = $('.' + user.uuid + ' .btn.undelete').button('loading');
        $scope.update(user, $btn);
    };
    $scope.update = function(user, $btn) {
        var index = $scope.getIndex(user.uuid);
        $http.post('/api/users/' + user.uuid, data=user).success(function(response) {
            $scope.updateUserList(index, response);
        }).finally(function() {
            $btn.button('reset');
        });
    };
    $scope.deleteUser = function(user) {
        var $btn = $('.' + user.uuid + ' .btn.delete-user').button('loading');
        var index = $scope.getIndex(user.uuid);
        $http.delete('/api/users/' + user.uuid).success(function(response) {
            $scope.updateUserList(index, response);
        }).finally(function() {
            $btn.button('reset');
        });
    };
    $scope.updateUserList = function(index, user) {
        if (index < 0) {
            $scope.users.push(user);
        } else {
            $scope.users[index] = user;
        }
    };
    $scope.getIndex = function(user_uuid) {
        var i;
        for (i = 0; i < $scope.users.length; i++) {
            if ($scope.users[i].uuid === user_uuid) {
                return i;
            }
        }
        return -1;
    };
}]);
