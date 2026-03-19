/**
 * controllers/dashboard.controller.ts — FIXED
 * Fixes: resumeCount stays 0 (async+$apply conflict), rank button disabled, word count
 */
angular.module("hireSenseApp").controller("DashboardController", ["$scope", "$rootScope", "$timeout",
    function ($scope, $rootScope, $timeout) {
        var api = window.ApiService;
        // ── State ──────────────────────────────────────────────────────────────
        $scope.jobDescription = "";
        $scope.resumes = [];
        $scope.ranked = [];
        $scope.analytics = null;
        $scope.loading = false;
        $scope.rankingDone = false;
        $scope.errorMsg = "";
        $scope.sortField = "rank";
        $scope.sortReverse = false;
        $scope.filterLevel = "All";
        $scope.resumeCount = 0;
        $scope.wordCount = 0;
        var scoreChart = null;
        var levelChart = null;
        // ── Word count watcher (fixes the word count not updating) ─────────────
        $scope.$watch("jobDescription", function (val) {
            if (!val || !val.trim()) {
                $scope.wordCount = 0;
            }
            else {
                $scope.wordCount = val.trim().split(/\s+/).length;
            }
        });
        // ── Load resumes — uses .then() to avoid async+$apply conflicts ────────
        $scope.loadResumes = function () {
            api.getResumes().then(function (res) {
                $scope.resumes = res.resumes;
                $scope.resumeCount = res.count;
                // Safe apply — only if not already in a digest cycle
                if (!$scope.$$phase) {
                    $scope.$apply();
                }
            }).catch(function (err) {
                $scope.errorMsg = "Could not load resumes: " + err.message;
                if (!$scope.$$phase) {
                    $scope.$apply();
                }
            });
        };
        // ── Init ───────────────────────────────────────────────────────────────
        $scope.loadResumes();
        // Refresh when upload controller signals new resumes
        $rootScope.$on("resumes:updated", function () {
            $scope.loadResumes();
        });
        // ── Rank — uses .then() chain ──────────────────────────────────────────
        $scope.rankCandidates = function () {
            var jd = ($scope.jobDescription || "").trim();
            if (!jd) {
                $scope.errorMsg = "Please enter a job description.";
                return;
            }
            if (!$scope.resumes || $scope.resumes.length === 0) {
                $scope.errorMsg = "Upload at least one resume before ranking.";
                return;
            }
            $scope.loading = true;
            $scope.errorMsg = "";
            $scope.rankingDone = false;
            api.rankCandidates(jd).then(function (result) {
                $scope.ranked = result.ranked;
                $scope.analytics = result.analytics;
                $scope.rankingDone = true;
                $scope.loading = false;
                if (!$scope.$$phase) {
                    $scope.$apply();
                }
                $timeout(function () { $scope._renderCharts(); }, 150);
            }).catch(function (err) {
                $scope.errorMsg = err.message;
                $scope.loading = false;
                if (!$scope.$$phase) {
                    $scope.$apply();
                }
            });
        };
        // ── Sorting ────────────────────────────────────────────────────────────
        $scope.sortBy = function (field) {
            if ($scope.sortField === field) {
                $scope.sortReverse = !$scope.sortReverse;
            }
            else {
                $scope.sortField = field;
                $scope.sortReverse = false;
            }
        };
        $scope.filteredRanked = function () {
            if ($scope.filterLevel === "All") {
                return $scope.ranked;
            }
            return $scope.ranked.filter(function (r) {
                return r.match_level === $scope.filterLevel;
            });
        };
        // ── Helpers ────────────────────────────────────────────────────────────
        $scope.scoreColor = function (score) {
            if (score >= 75) {
                return "#22c55e";
            }
            if (score >= 50) {
                return "#3b82f6";
            }
            if (score >= 25) {
                return "#f59e0b";
            }
            return "#ef4444";
        };
        $scope.levelClass = function (level) {
            var map = {
                Excellent: "badge-excellent",
                Good: "badge-good",
                Fair: "badge-fair",
                Low: "badge-low",
            };
            return map[level] || "";
        };
        // ── Charts ─────────────────────────────────────────────────────────────
        $scope._renderCharts = function () {
            if (!$scope.analytics) {
                return;
            }
            _renderScoreDistribution();
            _renderMatchLevels();
        };
        function _renderScoreDistribution() {
            var canvas = document.getElementById("scoreChart");
            if (!canvas) {
                return;
            }
            if (scoreChart) {
                scoreChart.destroy();
            }
            var buckets = $scope.analytics.score_buckets;
            scoreChart = new Chart(canvas, {
                type: "bar",
                data: {
                    labels: Object.keys(buckets),
                    datasets: [{
                            label: "Candidates",
                            data: Object.values(buckets),
                            backgroundColor: ["#ef4444", "#f59e0b", "#3b82f6", "#8b5cf6", "#22c55e"],
                            borderRadius: 6,
                            borderSkipped: false,
                        }],
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { display: false },
                        title: { display: true, text: "Score Distribution", color: "#e2e8f0", font: { size: 14 } },
                    },
                    scales: {
                        x: { ticks: { color: "#94a3b8" }, grid: { color: "#1e293b" } },
                        y: { ticks: { color: "#94a3b8", stepSize: 1 }, grid: { color: "#1e293b" }, beginAtZero: true },
                    },
                },
            });
        }
        function _renderMatchLevels() {
            var canvas = document.getElementById("levelChart");
            if (!canvas) {
                return;
            }
            if (levelChart) {
                levelChart.destroy();
            }
            var levels = $scope.analytics.match_levels;
            levelChart = new Chart(canvas, {
                type: "doughnut",
                data: {
                    labels: ["Excellent", "Good", "Fair", "Low"],
                    datasets: [{
                            data: [levels.Excellent, levels.Good, levels.Fair, levels.Low],
                            backgroundColor: ["#22c55e", "#3b82f6", "#f59e0b", "#ef4444"],
                            borderWidth: 0,
                            hoverOffset: 10,
                        }],
                },
                options: {
                    responsive: true,
                    cutout: "68%",
                    plugins: {
                        legend: { position: "bottom", labels: { color: "#94a3b8", padding: 14, font: { size: 12 } } },
                        title: { display: true, text: "Match Quality", color: "#e2e8f0", font: { size: 14 } },
                    },
                },
            });
        }
        // ── Delete ─────────────────────────────────────────────────────────────
        $scope.deleteResume = function (id) {
            if (!confirm("Delete this resume?")) {
                return;
            }
            api.deleteResume(id).then(function () {
                $scope.ranked = $scope.ranked.filter(function (r) { return r._id !== id; });
                $scope.loadResumes();
            }).catch(function (err) {
                $scope.errorMsg = err.message;
                if (!$scope.$$phase) {
                    $scope.$apply();
                }
            });
        };
    }]);
