/**
 * app.ts — HireSense AI  |  AngularJS application module
 */
angular.module("hireSenseApp", ["ngRoute"]).config([
    "$routeProvider",
    function ($routeProvider) {
        $routeProvider
            .when("/upload", {
            templateUrl: "views/upload.html",
            controller: "UploadController",
        })
            .when("/dashboard", {
            templateUrl: "views/dashboard.html",
            controller: "DashboardController",
        })
            .otherwise({ redirectTo: "/upload" });
    },
]);
// ── hs-file-input directive ───────────────────────────────────────────────────
// Proper Angular directive to handle <input type="file"> change events.
// Avoids the broken inline onchange="angular.element(this).scope()..." pattern.
angular.module("hireSenseApp").directive("hsFileInput", function () {
    return {
        restrict: "A",
        link: function (scope, element) {
            element.on("change", function (event) {
                var files = Array.prototype.slice.call(event.target.files || []);
                scope._addFiles(files);
                event.target.value = ""; // reset so same file can be re-selected
                if (!scope.$$phase) {
                    scope.$apply();
                }
            });
        },
    };
});
// ── Global run block ──────────────────────────────────────────────────────────
angular.module("hireSenseApp").run([
    "$rootScope",
    function ($rootScope) {
        $rootScope.appName = "HireSense AI";
        $rootScope.activeTab = "upload";
        $rootScope.setTab = function (tab) {
            $rootScope.activeTab = tab;
        };
    },
]);
