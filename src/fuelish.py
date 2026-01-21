<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Fuelish — Fuel Prices</title>
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
  <style>
    body { padding: 1.5rem; }
    .file-list { max-width: 320px; }
    .preview { margin-top: 1rem; }
    .dt-wrapper { width: 100%; overflow-x: auto; }
  </style>
</head>
<body>
  <div class="container">
    <h1 class="mb-3">Fuelish — Fuel Prices (CSV)</h1>

    <div class="row">
      <div class="col-md-4">
        <div class="card file-list">
          <div class="card-body">
            <h5 class="card-title">Available CSVs</h5>
            <ul id="csv-list" class="list-group list-group-flush"></ul>
            <div class="mt-2">
              <button id="refresh-list" class="btn btn-sm btn-secondary">Refresh</button>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-8">
        <div id="preview-wrapper" class="card preview">
          <div class="card-body">
            <h5 id="preview-title" class="card-title">Select a CSV to preview</h5>
            <div id="preview-controls" class="mb-2" style="display:none;">
              <a id="download-link" class="btn btn-sm btn-outline-primary" href="#" download>Download CSV</a>
            </div>
            <div class="dt-wrapper">
              <table id="preview-table" class="display" style="width:100%"></table>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>

  <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
  <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>

  <script>
    const listEl = document.getElementById('csv-list');
    const previewTitle = document.getElementById('preview-title');
    const previewTable = $('#preview-table');
    const previewControls = document.getElementById('preview-controls');
    const downloadLink = document.getElementById('download-link');
    let dataTable = null;

    async function loadList() {
      listEl.innerHTML = '';
      const res = await fetch('/api/list');
      const items = await res.json();
      if (items.length === 0) {
        listEl.innerHTML = '<li class="list-group-item">No CSVs found. Run the scraper first.</li>';
        return;
      }
      for (const it of items) {
        const li = document.createElement('li');
        li.className = 'list-group-item d-flex justify-content-between align-items-center';
        li.innerHTML = `<span>${it.label}</span><button data-file="${it.file}" class="btn btn-sm btn-primary preview-btn">Preview</button>`;
        listEl.appendChild(li);
      }
      // attach handlers
      document.querySelectorAll('.preview-btn').forEach(btn => {
        btn.addEventListener('click', () => previewCSV(btn.dataset.file));
      });
    }

    async function previewCSV(file) {
      previewTitle.textContent = 'Loading...';
      previewControls.style.display = 'none';
      // fetch CSV JSON
      const res = await fetch(`/api/csv/${encodeURIComponent(file)}`);
      if (!res.ok) {
        previewTitle.textContent = 'Error loading CSV';
        return;
      }
      const payload = await res.json();
      const header = payload.header || [];
      const rows = payload.rows || [];
      previewTitle.textContent = file.replace('.csv','').replace(/-/g,' ').toUpperCase();

      downloadLink.href = `/assets/${file}`;
      downloadLink.style.display = 'inline-block';
      previewControls.style.display = 'block';

      // destroy DataTable if exists
      if ($.fn.DataTable.isDataTable('#preview-table')) {
        previewTable.DataTable().destroy();
        previewTable.empty();
      }

      // build table head
      let thead = '<thead><tr>';
      for (const h of header) thead += `<th>${h}</th>`;
      thead += '</tr></thead>';
      previewTable.append(thead);

      // build table body
      let tbody = '<tbody>';
      for (const r of rows) {
        tbody += '<tr>';
        for (const c of r) tbody += `<td>${c}</td>`;
        tbody += '</tr>';
      }
      tbody += '</tbody>';
      previewTable.append(tbody);

      dataTable = previewTable.DataTable({
        pageLength: 10,
        lengthChange: false,
        columns: header.map(() => ({ searchable: true })),
        order: [],
      });
    }

    document.getElementById('refresh-list').addEventListener('click', loadList);

    // initial load
    loadList();
  </script>
</body>
</html>
