/* ------------------------------------------------------------------
   viz.js
   Author: Student 6
   Renders all charts on the Data Visualisation page.
   Uses Chart.js 4. All datasets come from the #vizPayload JSON block.
   ------------------------------------------------------------------ */
(function () {
  'use strict';

  var payloadEl = document.getElementById('vizPayload');
  if (!payloadEl) { console.error('[viz] payload element not found'); return; }
  var data;
  try { data = JSON.parse(payloadEl.textContent); }
  catch (err) { console.error('[viz] failed to parse payload JSON', err); return; }

  var PALETTE = [
    '#0057B8', '#00A0DC', '#66C0E8', '#004E92',
    '#5AC8FA', '#FFC300', '#FF6B6B', '#2ECC71',
    '#9B59B6', '#34495E', '#E67E22', '#1ABC9C',
  ];
  function colour(i) { return PALETTE[i % PALETTE.length]; }

  var commonOpts = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: true, position: 'bottom' },
      tooltip: { mode: 'index', intersect: false },
    },
  };

  // Chart 1: Teams per Department
  new Chart(document.getElementById('chartTeamsPerDept'), {
    type: 'bar',
    data: {
      labels: data.teamsPerDept.labels,
      datasets: [{ label: 'Teams', data: data.teamsPerDept.data,
        backgroundColor: data.teamsPerDept.labels.map(function(_, i){ return colour(i); }) }],
    },
    options: Object.assign({}, commonOpts, {
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
    }),
  });

  // Chart 2: Head vs Projects
  new Chart(document.getElementById('chartHeadVsProjects'), {
    type: 'bar',
    data: {
      labels: data.headVsProjects.labels,
      datasets: [{ label: 'Projects', data: data.headVsProjects.data,
        backgroundColor: '#0057B8' }],
    },
    options: Object.assign({}, commonOpts, {
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
    }),
  });

  // Chart 3: Stacked
  var stacked = data.deptProjectsStack;
  new Chart(document.getElementById('chartDeptProjectsStack'), {
    type: 'bar',
    data: {
      labels: stacked.labels,
      datasets: stacked.datasets.map(function(ds, i){
        return { label: ds.label, data: ds.data,
          backgroundColor: colour(i), borderColor: '#fff', borderWidth: 1 };
      }),
    },
    options: Object.assign({}, commonOpts, {
      scales: {
        x: { stacked: true },
        y: { stacked: true, beginAtZero: true, ticks: { precision: 0 } },
      },
      plugins: { legend: { position: 'bottom',
        labels: { boxWidth: 12, font: { size: 10 } } } },
    }),
  });

  // Chart 4: Members per team
  new Chart(document.getElementById('chartMembersPerTeam'), {
    type: 'bar',
    data: {
      labels: data.membersPerTeam.labels,
      datasets: [{ label: 'Members', data: data.membersPerTeam.data,
        backgroundColor: '#00A0DC' }],
    },
    options: Object.assign({}, commonOpts, {
      indexAxis: 'y',
      plugins: { legend: { display: false } },
      scales: { x: { beginAtZero: true, ticks: { precision: 0 } } },
    }),
  });

  // Chart 5: Dependency types
  new Chart(document.getElementById('chartDependencyTypes'), {
    type: 'doughnut',
    data: {
      labels: data.dependencyTypes.labels,
      datasets: [{
        data: data.dependencyTypes.data,
        backgroundColor: data.dependencyTypes.labels.map(function(_, i){ return colour(i); }),
      }],
    },
    options: Object.assign({}, commonOpts, { cutout: '55%' }),
  });

  // Chart 6: Concurrent projects
  new Chart(document.getElementById('chartConcurrent'), {
    type: 'bar',
    data: {
      labels: data.concurrent.labels,
      datasets: [{ label: 'Concurrent projects', data: data.concurrent.data,
        backgroundColor: '#FFC300' }],
    },
    options: Object.assign({}, commonOpts, {
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
    }),
  });
})();