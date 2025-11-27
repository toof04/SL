
    


let chartDoodler = null;
let showValFlag = false;

let recallPack = {
    spot: '',
    fname: '',
    chunk: '',
    ctype: '',
    labs: [],
    vals: [],
    blobArr: null,
    isSeries: false,
    endpoint: ''
};

function splashColors(ct) {
    let stash = [];
    for (let q = 0; q < ct; q++) {
        let h = (q * 29) % 360;
        stash.push(`hsl(${h},73%,61%)`);
    }
    return stash;
}

async function pullJson(u) {
    let r = await fetch(u);
    if (!r.ok) {
        let tx = await r.text();
        throw new Error(tx || r.statusText);
    }
    return r.json();
}

function clearChartBox() {
    if (chartDoodler) {
        try { chartDoodler.destroy(); } catch (_) {}
        chartDoodler = null;
    }
}

async function revealCsvBit(sp, fn) {
    let pane = document.getElementById('csvDataContainer');
    let hd = document.getElementById('csvTableHead');
    let bd = document.getElementById('csvTableBody');

    if (!sp && !fn) {
        pane.style.display = 'none';
        return;
    }

    try {
        let link = '/api/csv/data?subpath=' + encodeURIComponent(sp) + '&file=' + encodeURIComponent(fn);
        let getit = await pullJson(link);

        if (getit && getit.error) {
            pane.style.display = 'none';
            return;
        }

        hd.innerHTML = '';
        bd.innerHTML = '';

        let hr = document.createElement('tr');
        getit.columns.forEach(c => {
            let th = document.createElement('th');
            th.textContent = c;
            th.style.padding = '8px';
            hr.appendChild(th);
        });
        hd.appendChild(hr);

        getit.data.forEach(row => {
            let tr = document.createElement('tr');
            getit.columns.forEach(c => {
                let td = document.createElement('td');
                td.textContent = row[c] || '';
                td.style.padding = '6px 8px';
                tr.appendChild(td);
            });
            bd.appendChild(tr);
        });

        let alt = bd.querySelectorAll('tr');
        for (let i = 0; i < alt.length; i++) {
            if (i % 2 === 0) alt[i].style.backgroundColor = '#f9f9f9';
        }

        pane.style.display = 'block';
    } catch {
        pane.style.display = 'none';
    }
}

function toggleDatalabels() {
    if (showValFlag) {
        return { datalabels: { color: '#333', anchor: 'end', align: 'end' } };
    }
    return { datalabels: { display: false } };
}

function dropSort(l, v) {
    if (!Array.isArray(l) || !Array.isArray(v)) return [l, v];
    let pack = [];
    for (let x = 0; x < l.length; x++) {
        pack.push({ a: l[x], b: Number(v[x]) || 0 });
    }
    pack.sort((aa, bb) => bb.b - aa.b);
    return [pack.map(o => o.a), pack.map(o => o.b)];
}

function paintChart(kind, labs, valset, ttl) {
    let c = document.getElementById('mainChart').getContext('2d');
    clearChartBox();

    if (kind === 'bar') {
        let sorted = dropSort(labs, valset);
        labs = sorted[0];
        valset = sorted[1];
    }

    let rotx = { ticks: { minRotation: 90, maxRotation: 90 } };
    let yr = { ticks: { beginAtZero: true } };

    let opt = {
        responsive: true,
        animation: { duration: 500 },
        plugins: Object.assign({}, toggleDatalabels(), {
            tooltip: {
                callbacks: {
                    label: (ctx) => {
                        let L = ctx.label || '';
                        let v = ctx.raw;
                        return L + ': ' + v;
                    }
                }
            }
        })
    };

    let cfg = {
        type:
            kind === 'multiline' ? 'line' :
            (kind === 'groupedbar' || kind === 'stackedbar' ? 'bar' : kind),
        data: { labels: labs, datasets: [] },
        plugins: [ChartDataLabels],
        options: opt
    };

    if (kind === 'multiline' && Array.isArray(valset)) {
        let pal = splashColors(valset.length);
        cfg.data.datasets = valset.map((s, i) => ({
            label: s.label,
            data: s.data,
            borderWidth: 2,
            tension: 0.2,
            fill: false,
            borderColor: pal[i],
            backgroundColor: pal[i],
            pointRadius: 3
        }));
        cfg.options.scales = { x: rotx, y: yr };
    } else if (kind === 'groupedbar') {
        let pal = splashColors(valset.length);
        cfg.data.datasets = valset.map((s, i) => ({
            label: s.label,
            data: s.data,
            backgroundColor: pal[i],
            borderRadius: 6
        }));
        cfg.options.scales = { x: rotx, y: yr };
    } else if (kind === 'stackedbar') {
        let pal = splashColors(valset.length);
        cfg.data.datasets = valset.map((s, i) => ({
            label: s.label,
            data: s.data,
            backgroundColor: pal[i],
            borderRadius: 6
        }));
        cfg.options.scales = {
            x: { ...rotx, stacked: true },
            y: { ...yr, stacked: true }
        };
    } else if (kind === 'line') {
        let one = splashColors(1)[0];
        cfg.data.datasets = [{
            label: ttl,
            data: valset,
            borderWidth: 2,
            tension: 0.2,
            fill: false,
            borderColor: one,
            backgroundColor: one,
            pointRadius: 3
        }];
        cfg.options.scales = { x: rotx, y: yr };
    } else if (kind === 'bar') {
        cfg.data.datasets = [{
            label: ttl,
            data: valset,
            backgroundColor: splashColors(valset.length),
            borderRadius: 6
        }];
        cfg.options.scales = { x: rotx, y: yr };
    } else if (kind === 'pie') {
        let sorted = dropSort(labs, valset);
        cfg.data.labels = sorted[0];
        cfg.data.datasets = [{
            label: ttl,
            data: sorted[1],
            backgroundColor: splashColors(sorted[1].length)
        }];
    }

    chartDoodler = new Chart(c, cfg);
}

function flipToggles() {
    let ctn = document.getElementById('chartToggleContainer');
    let bbtn = document.getElementById('barBtn');
    let pbtn = document.getElementById('pieBtn');
    if (!ctn || !bbtn || !pbtn) return;

    if (recallPack.isSeries || recallPack.ctype === 'groupedbar' || recallPack.ctype === 'stackedbar') {
        ctn.classList.add('hidden');
        bbtn.classList.remove('activeToggle');
        pbtn.classList.remove('activeToggle');
        return;
    }

    ctn.classList.remove('hidden');
    if (recallPack.ctype === 'pie') {
        pbtn.classList.add('activeToggle');
        bbtn.classList.remove('activeToggle');
    } else {
        bbtn.classList.add('activeToggle');
        pbtn.classList.remove('activeToggle');
    }
}

async function changeChartMode(ov) {
    if (recallPack.isSeries) return;

    if (recallPack.endpoint === 'total_default') {
        recallPack.ctype = ov;
        if (recallPack.ctype === 'multiline') {
            paintChart('multiline', recallPack.labs, recallPack.blobArr, recallPack.fname || '');
        } else {
            paintChart(recallPack.ctype, recallPack.labs, recallPack.vals, recallPack.fname || '');
        }
        flipToggles();
        return;
    }

    if (recallPack.spot && recallPack.fname) {
        try {
            await bringFile(recallPack.spot, recallPack.fname, recallPack.chunk, ov);
        } catch (e) {}
    } else {
        recallPack.ctype = ov;
        if (recallPack.ctype === 'multiline') {
            paintChart('multiline', recallPack.labs, recallPack.blobArr, recallPack.fname || '');
        } else {
            paintChart(recallPack.ctype, recallPack.labs, recallPack.vals, recallPack.fname || '');
        }
        flipToggles();
    }
}

function callMain(sec) {
    let a = document.getElementById('crimeMainSection');
    let b = document.getElementById('literacyMainSection');
    let c = document.getElementById('roadwaysMainSection');
    let d = document.getElementById('labourMainSection');
    let ba = document.getElementById('btnMainCrime');
    let bb = document.getElementById('btnMainLiteracy');
    let bc = document.getElementById('btnMainRoadways');
    let bd = document.getElementById('btnMainLabour');

    a.classList.add('hidden');
    b.classList.add('hidden');
    c.classList.add('hidden');
    d.classList.add('hidden');
    ba.classList.remove('active');
    bb.classList.remove('active');
    bc.classList.remove('active');
    bd.classList.remove('active');

    if (sec === 'crime') {
        a.classList.remove('hidden');
        ba.classList.add('active');
        swapCrime('total');
    } else if (sec === 'literacy') {
        b.classList.remove('hidden');
        bb.classList.add('active');
        swapLiter('schools');
    } else if (sec === 'roadways') {
        c.classList.remove('hidden');
        bc.classList.add('active');
        clearChartBox();
    } else if (sec === 'labour') {
        d.classList.remove('hidden');
        bd.classList.add('active');
        swapLab('statewise');
    }
}

function swapCrime(sub) {
    let mp = {
        total: document.getElementById('totalSection'),
        religion: document.getElementById('religionSection'),
        women: document.getElementById('womenSection'),
        education: document.getElementById('educationSection'),
        caste: document.getElementById('casteSection'),
        police: document.getElementById('policeSection'),
        children: document.getElementById('childrenSection')
    };
    let bp = {
        total: document.getElementById('btnTotal'),
        religion: document.getElementById('btnReligion'),
        women: document.getElementById('btnWomen'),
        education: document.getElementById('btnEducation'),
        caste: document.getElementById('btnCaste'),
        police: document.getElementById('btnPolice'),
        children: document.getElementById('btnChildren')
    };

    Object.values(mp).forEach(el => el.classList.add('hidden'));
    Object.values(bp).forEach(bb => bb.classList.remove('active'));

    if (mp[sub]) mp[sub].classList.remove('hidden');
    if (bp[sub]) bp[sub].classList.add('active');

    clearDrops();
    clearChartBox();

    if (sub === 'total') grabTotalDefault();
}

function swapLiter(nu) {
    let mp = {
        schools: document.getElementById('schoolsSection'),
        logistics: document.getElementById('logisticsSection'),
        rates: document.getElementById('ratesSection')
    };
    let bp = {
        schools: document.getElementById('btnSchools'),
        logistics: document.getElementById('btnLogistics'),
        rates: document.getElementById('btnRates')
    };

    Object.values(mp).forEach(el => el.classList.add('hidden'));
    Object.values(bp).forEach(bb => bb.classList.remove('active'));

    if (mp[nu]) mp[nu].classList.remove('hidden');
    if (bp[nu]) bp[nu].classList.add('active');

    wipeLiterDrops();
    clearChartBox();
}

function swapLab(g) {
    let mp = {
        statewise: document.getElementById('statewiseSection'),
        occupation: document.getElementById('occupationSection'),
        ageGender: document.getElementById('ageGenderSection')
    };
    let bp = {
        statewise: document.getElementById('btnStatewise'),
        occupation: document.getElementById('btnOccupation'),
        ageGender: document.getElementById('btnAgeGender')
    };

    Object.values(mp).forEach(el => el.classList.add('hidden'));
    Object.values(bp).forEach(bb => bb.classList.remove('active'));

    if (mp[g]) mp[g].classList.remove('hidden');
    if (bp[g]) bp[g].classList.add('active');

    if (g === 'statewise') {
        swapStatewiseSub('jobSeekers');
    }
    clearChartBox();
}

function swapStatewiseSub(n) {
    let j = document.getElementById('jobSeekersSection');
    let r = document.getElementById('registeredSection');
    let bj = document.getElementById('btnJobSeekers');
    let br = document.getElementById('btnRegistered');

    if (n === 'jobSeekers') {
        j.classList.remove('hidden');
        r.classList.add('hidden');
        bj.classList.add('active');
        br.classList.remove('active');
    } else {
        j.classList.add('hidden');
        r.classList.remove('hidden');
        bj.classList.remove('active');
        br.classList.add('active');
    }
}

function softReset(sel) {
    if (!sel) return;
    sel.selectedIndex = 0;
    sel.classList.remove('active-select');
}

function clearDrops() {
    let ls = [
        'top10Select','bottom10Select','timeSeriesSelect',
        'religionTopFiles','religionBottomFiles','religionStates','religionByReligion',
        'womenStates','womenCrimeTypes','womenTimeSeries',
        'educationGraphs','educationStates',
        'casteConvTop','casteConvBottom','casteConvStateDist','casteDetTop','casteDetStateTotal',
        'policeTop','policePercents',
        'childrenTopStates','childrenTopCrime'
    ];
    ls.forEach(id => softReset(document.getElementById(id)));

    document.getElementById('casteConvictsControls').classList.remove('hidden');
    document.getElementById('casteDetenuesControls')?.classList.add('hidden');
    let radios = document.getElementsByName('casteMode');
    radios.forEach(r => r.checked = (r.value === 'convicts'));
}

function wipeLiterDrops() {
    let arr = [
        'schoolsState','schoolsBest','schoolsWorst',
        'dropoutCategory','dropoutSubSelect',
        'literacyTop','literacyBottom','literacyState',
        'yearSchoolTop','yearSchoolBottom','yearSchoolState'
    ];
    arr.forEach(s => softReset(document.getElementById(s)));

    document.getElementById('schoolLevelControls').classList.add('hidden');
    document.getElementById('dropoutSubControls').classList.add('hidden');

    let gg = document.getElementsByName('schoolLevel');
    gg.forEach(r => r.checked = false);

    let rr = document.getElementsByName('rateType');
    rr.forEach(r => r.checked = (r.value === 'dropout'));

    document.getElementById('dropoutControls').classList.remove('hidden');
    document.getElementById('literacyRateControls').classList.add('hidden');
    document.getElementById('yearSchoolControls').classList.add('hidden');
}

function flagActive(s) {
    document.querySelectorAll('select').forEach(x => x.classList.remove('active-select'));
    if (s) s.classList.add('active-select');
}

function wipeSome(section, skip = []) {
    let lp = {
        total: ['top10Select','bottom10Select','timeSeriesSelect'],
        religion: ['religionTopFiles','religionBottomFiles','religionStates','religionByReligion'],
        women: ['womenStates','womenCrimeTypes','womenTimeSeries'],
        education: ['educationGraphs','educationStates'],
        caste: ['casteConvTop','casteConvBottom','casteConvStateDist','casteDetTop','casteDetStateTotal'],
        police: ['policeTop','policePercents'],
        children: ['childrenTopStates','childrenTopCrime']
    };
    (lp[section] || []).forEach(id => { if (!skip.includes(id)) softReset(document.getElementById(id)); });
}

function stashRecall(obj) {
    recallPack = Object.assign({}, recallPack, obj);
    recallPack.isSeries = ['line','multiline'].includes(recallPack.ctype);
    flipToggles();
}
/* CRIME HANDLERS – continuing in order 

async function fillTotals() {
    try {
        let top = await pullJson('/api/list?subpath=crime/total_crime/top_10');
        let sel = document.getElementById('top10Select');
        sel.innerHTML = '<option value="">-- choose top10 --</option>';
        top.files.forEach(f => {
            let o = document.createElement('option');
            o.value = f; o.textContent = f;
            sel.appendChild(o);
        });
        sel.onchange = function () {
            if (this.value) {
                flagActive(this);
                bringFile('crime/total_crime/top_10', this.value, 'total');
                wipeSome('total', ['top10Select']);
            }
        };
    } catch (_) {}

    try {
        let bot = await pullJson('/api/list?subpath=crime/total_crime/bottom_10');
        let sel = document.getElementById('bottom10Select');
        sel.innerHTML = '<option value="">-- choose bottom10 --</option>';
        bot.files.forEach(f => {
            let o = document.createElement('option');
            o.value = f; o.textContent = f;
            sel.appendChild(o);
        });
        sel.onchange = function () {
            if (this.value) {
                flagActive(this);
                bringFile('crime/total_crime/bottom_10', this.value, 'total');
                wipeSome('total', ['bottom10Select']);
            }
        };
    } catch (_) {}

    try {
        let ts = await pullJson('/api/list?subpath=crime/total_crime/time_series');
        let sel = document.getElementById('timeSeriesSelect');
        sel.innerHTML = '<option value="">-- choose state series --</option>';
        ts.files.forEach(f => {
            let o = document.createElement('option');
            o.value = f; o.textContent = f;
            sel.appendChild(o);
        });
        sel.onchange = function () {
            if (this.value) {
                flagActive(this);
                bringFile('crime/total_crime/time_series', this.value, 'total');
                wipeSome('total', ['timeSeriesSelect']);
            }
        };
    } catch (_) {}

    await grabTotalDefault();
}

async function grabTotalDefault() {
    try {
        clearDrops();
        let out = await pullJson('/api/plot/total_default');
        paintChart('bar', out.labels, out.values, 'Total Crime (2020–2022)');
        stashRecall({
            endpoint: 'total_default',
            spot: 'crime/total_crime/default',
            fname: 'default.csv',
            chunk: 'total',
            ctype: 'bar',
            labs: out.labels,
            vals: out.values,
            blobArr: null
        });
        await revealCsvBit('crime/total_crime/default', 'default.csv');
    } catch (e) {}
}

async function fillReligion() {
    let btn = document.getElementById('religionDefaultBtn');
    btn.onclick = async () => {
        clearDrops();
        try {
            let list = await pullJson('/api/list?subpath=crime/religion/default');
            let pick = (list.files && list.files.length > 0) ? list.files[0] : 'default.csv';

            let got = await pullJson('/api/plot/file?subpath=crime/religion/default&file=' + encodeURIComponent(pick));
            if (got.chartType === 'stackedbar' && got.series) {
                paintChart('stackedbar', got.labels, got.series, 'Religion – States');
                stashRecall({
                    spot: 'crime/religion/default',
                    fname: pick,
                    chunk: 'religion',
                    ctype: 'stackedbar',
                    labs: got.labels,
                    blobArr: got.series
                });
            } else if (got.chartType === 'pie') {
                paintChart('pie', got.labels, got.values, 'Religion % of India');
                stashRecall({
                    spot: 'crime/religion/default',
                    fname: pick,
                    chunk: 'religion',
                    ctype: 'pie',
                    labs: got.labels,
                    vals: got.values
                });
            }
            await revealCsvBit('crime/religion/default', pick);
        } catch (err) {}
    };

    try {
        let top = await pullJson('/api/list?subpath=crime/religion/top');
        let sel = document.getElementById('religionTopFiles');
        sel.innerHTML = '<option value="">-- top5 --</option>';
        top.files.forEach(f => {
            let o = document.createElement('option');
            o.value = f; o.textContent = f;
            sel.appendChild(o);
        });
        sel.onchange = function () {
            if (this.value) {
                flagActive(this);
                bringFile('crime/religion/top', this.value, 'religion');
                wipeSome('religion', ['religionTopFiles']);
            }
        };
    } catch (_) {}

    try {
        let bot = await pullJson('/api/list?subpath=crime/religion/bottom');
        let sel = document.getElementById('religionBottomFiles');
        sel.innerHTML = '<option value="">-- bottom5 --</option>';
        bot.files.forEach(f => {
            let o = document.createElement('option');
            o.value = f; o.textContent = f;
            sel.appendChild(o);
        });
        sel.onchange = function () {
            if (this.value) {
                flagActive(this);
                bringFile('crime/religion/bottom', this.value, 'religion');
                wipeSome('religion', ['religionBottomFiles']);
            }
        };
    } catch (_) {}

    try {
        let st = await pullJson('/api/list?subpath=crime/religion/states');
        let sel = document.getElementById('religionStates');
        sel.innerHTML = '<option value="">-- by state --</option>';
        st.files.forEach(f => {
            let o = document.createElement('option');
            o.value = f; o.textContent = f;
            sel.appendChild(o);
        });
        sel.onchange = function () {
            if (this.value) {
                flagActive(this);
                bringFile('crime/religion/states', this.value, 'religion');
                wipeSome('religion', ['religionStates']);
            }
        };
    } catch (_) {}

    try {
        let byR = await pullJson('/api/list?subpath=crime/religion/religion');
        let sel = document.getElementById('religionByReligion');
        sel.innerHTML = '<option value="">-- by religion --</option>';
        byR.files.forEach(f => {
            let o = document.createElement('option');
            o.value = f; o.textContent = f;
            sel.appendChild(o);
        });
        sel.onchange = function () {
            if (this.value) {
                flagActive(this);
                bringFile('crime/religion/religion', this.value, 'religion');
                wipeSome('religion', ['religionByReligion']);
            }
        };
    } catch (_) {}
}

async function fillWomen() {
    document.getElementById('womenDefaultBtn').onclick = async () => {
        clearDrops();
        try {
            let out = await pullJson('/api/plot/file?subpath=crime/women/default&file=state_total.csv');
            paintChart('bar', out.labels, out.values, 'Women – State Total');
            stashRecall({
                spot: 'crime/women/default',
                fname: 'state_total.csv',
                chunk: 'women',
                ctype: 'bar',
                labs: out.labels,
                vals: out.values
            });
            await revealCsvBit('crime/women/default', 'state_total.csv');
        } catch (_) {}
    };

    try {
        let st = await pullJson('/api/list?subpath=crime/women/states');
        let sel = document.getElementById('womenStates');
        sel.innerHTML = '<option value="">-- pick state --</option>';
        st.files.forEach(f => {
            let o = document.createElement('option'); o.value = f; o.textContent = f;
            sel.appendChild(o);
        });
        sel.onchange = () => {
            if (sel.value) {
                flagActive(sel);
                bringFile('crime/women/states', sel.value, 'women');
                wipeSome('women', ['womenStates']);
            }
        };
    } catch (_) {}

    try {
        let ct = await pullJson('/api/list?subpath=crime/women/Crime_types');
        let sel = document.getElementById('womenCrimeTypes');
        sel.innerHTML = '<option value="">-- crime-type --</option>';
        ct.files.forEach(f => {
            let o=document.createElement('option'); o.value=f; o.textContent=f; sel.appendChild(o);
        });
        sel.onchange = () => {
            if (sel.value) {
                flagActive(sel);
                bringFile('crime/women/Crime_types', sel.value, 'women');
                wipeSome('women', ['womenCrimeTypes']);
            }
        };
    } catch (_) {}

    try {
        let ts = await pullJson('/api/list?subpath=crime/women/time_series');
        let sel = document.getElementById('womenTimeSeries');
        sel.innerHTML = '<option value="">-- time series --</option>';
        ts.files.forEach(f => {
            let o=document.createElement('option'); o.value=f; o.textContent=f;
            sel.appendChild(o);
        });
        sel.onchange = async function () {
            if (!this.value) return;
            flagActive(this);
            try {
                let out = await pullJson('/api/plot/file?subpath=crime/women/time_series&file=' + encodeURIComponent(this.value));
                if (out.chartType === 'multiline' && out.series) {
                    paintChart('multiline', out.labels, out.series, this.value.replace('.csv',''));
                    stashRecall({
                        spot: 'crime/women/time_series',
                        fname: this.value,
                        chunk: 'women',
                        ctype: 'multiline',
                        labs: out.labels,
                        blobArr: out.series
                    });
                } else {
                    let fallback = out.chartType || 'line';
                    paintChart(fallback, out.labels, out.values, this.value.replace('.csv',''));
                    stashRecall({
                        spot: 'crime/women/time_series',
                        fname: this.value,
                        chunk: 'women',
                        ctype: fallback,
                        labs: out.labels,
                        vals: out.values
                    });
                }
                await revealCsvBit('crime/women/time_series', this.value);
                wipeSome('women', ['womenTimeSeries']);
            } catch (_) {}
        };
    } catch (_) {}
}

async function fillEduCrime() {
    try {
        let lp = await pullJson('/api/list?subpath=crime/education/education');
        let sel = document.getElementById('educationGraphs');
        sel.innerHTML = '<option value="">-- graph --</option>';
        lp.files.forEach(f=>{
            let o=document.createElement('option');
            o.value=f; o.textContent=f; sel.appendChild(o);
        });
        sel.onchange = () => {
            if (sel.value) {
                flagActive(sel);
                bringFile('crime/education/education', sel.value, 'education');
                wipeSome('education', ['educationGraphs']);
            }
        };
    } catch (_) {}

    try {
        let st = await pullJson('/api/list?subpath=crime/education/state');
        let sel = document.getElementById('educationStates');
        sel.innerHTML = '<option value="">-- pick state --</option>';
        st.files.forEach(f=>{
            let o=document.createElement('option');
            o.value=f; o.textContent=f; sel.appendChild(o);
        });
        sel.onchange = () => {
            if (sel.value) {
                flagActive(sel);
                bringFile('crime/education/state', sel.value, 'education');
                wipeSome('education', ['educationStates']);
            }
        };
    } catch (_) {}
}

async function fillChildren() {
    document.getElementById('childrenDefaultBtn').onclick = async () => {
        clearDrops();
        try {
            let out = await pullJson('/api/plot/file?subpath=crime/children/default&file=default.csv');
            paintChart('bar', out.labels, out.values, 'Children – Summary');
            stashRecall({
                spot: 'crime/children/default',
                fname: 'default.csv',
                chunk: 'children',
                ctype: 'bar',
                labs: out.labels,
                vals: out.values
            });
            await revealCsvBit('crime/children/default', 'default.csv');
        } catch (_) {}
    };

    try {
        let lst = await pullJson('/api/list?subpath=crime/children/TopStates');
        let sel = document.getElementById('childrenTopStates');
        sel.innerHTML = '<option value="">-- TopStates --</option>';
        lst.files.forEach(f=>{
            let o=document.createElement('option');
            o.value=f; o.textContent=f; sel.appendChild(o);
        });
        sel.onchange = () => {
            if (sel.value) {
                flagActive(sel);
                bringFile('crime/children/TopStates', sel.value, 'children');
                wipeSome('children', ['childrenTopStates']);
            }
        };
    } catch (_) {}

    try {
        let lst = await pullJson('/api/list?subpath=crime/children/TopCrime');
        let sel = document.getElementById('childrenTopCrime');
        sel.innerHTML = '<option value="">-- TopCrime --</option>';
        lst.files.forEach(f=>{
            let o=document.createElement('option');
            o.value=f; o.textContent=f; sel.appendChild(o);
        });
        sel.onchange = () => {
            if (sel.value) {
                flagActive(sel);
                bringFile('crime/children/TopCrime', sel.value, 'children');
                wipeSome('children', ['childrenTopCrime']);
            }
        };
    } catch (_) {}
}

/* CASTE, POLICE, and LOAD-FILE HANDLERS – continuing in sequence 

async function fillCaste() {
    let radios = document.getElementsByName('casteMode');
    radios.forEach(r => {
        r.addEventListener('change', () => {
            let pick = document.querySelector('input[name="casteMode"]:checked')?.value;
            if (!pick) return;

            if (pick === 'convicts') {
                document.getElementById('casteConvictsControls').classList.remove('hidden');
                document.getElementById('casteDetenuesControls').classList.add('hidden');
                wipeOne('casteDetTop'); wipeOne('casteDetStateTotal');
            } else {
                document.getElementById('casteConvictsControls').classList.add('hidden');
                document.getElementById('casteDetenuesControls').classList.remove('hidden');
                wipeOne('casteConvTop'); wipeOne('casteConvBottom'); wipeOne('casteConvStateDist');
            }
        });
    });

    try {
        let lst = await pullJson('/api/list?subpath=crime/caste/caste_convicts_analysis/caste/top');
        let sel = document.getElementById('casteConvTop');
        sel.innerHTML = '<option value="">-- top5 --</option>';
        lst.files.forEach(f=>{
            let o=document.createElement('option'); o.value=f; o.textContent=f;
            sel.appendChild(o);
        });
        sel.onchange = () => {
            if (sel.value) {
                flagActive(sel);
                bringFile('crime/caste/caste_convicts_analysis/caste/top', sel.value, 'caste');
                wipeSome('caste', ['casteConvTop']);
            }
        };
    } catch (_) {}

    try {
        let lst = await pullJson('/api/list?subpath=crime/caste/caste_convicts_analysis/caste/bottom');
        let sel = document.getElementById('casteConvBottom');
        sel.innerHTML = '<option value="">-- bottom5 --</option>';
        lst.files.forEach(f=>{
            let o=document.createElement('option'); o.value=f; o.textContent=f;
            sel.appendChild(o);
        });
        sel.onchange = () => {
            if (sel.value) {
                flagActive(sel);
                bringFile('crime/caste/caste_convicts_analysis/caste/bottom', sel.value, 'caste');
                wipeSome('caste', ['casteConvBottom']);
            }
        };
    } catch (_) {}

    try {
        let lst = await pullJson('/api/list?subpath=crime/caste/caste_convicts_analysis/caste/caste');
        let sel = document.getElementById('casteConvStateDist');
        sel.innerHTML = '<option value="">-- state dist --</option>';
        lst.files.forEach(f=>{
            let o=document.createElement('option'); o.value=f; o.textContent=f;
            sel.appendChild(o);
        });
        sel.onchange = () => {
            if (sel.value) {
                flagActive(sel);
                bringFile('crime/caste/caste_convicts_analysis/caste/caste', sel.value, 'caste');
                wipeSome('caste', ['casteConvStateDist']);
            }
        };
    } catch (_) {}

    try {
        let lst = await pullJson('/api/list?subpath=crime/caste/detenues_caste_analysis/caste');
        let sel = document.getElementById('casteDetTop');
        sel.innerHTML = '<option value="">-- top5 --</option>';
        lst.files.forEach(f=>{
            let o=document.createElement('option'); o.value=f; o.textContent=f;
            sel.appendChild(o);
        });
        sel.onchange = () => {
            if (sel.value) {
                flagActive(sel);
                bringFile('crime/caste/detenues_caste_analysis/caste', sel.value, 'caste');
                wipeSome('caste', ['casteDetTop']);
            }
        };
    } catch (_) {}

    try {
        let lst = await pullJson('/api/list?subpath=crime/caste/detenues_caste_analysis/state');
        let sel = document.getElementById('casteDetStateTotal');
        sel.innerHTML = '<option value="">-- state total --</option>';
        lst.files.forEach(f=>{
            let o=document.createElement('option'); o.value=f; o.textContent=f;
            sel.appendChild(o);
        });
        sel.onchange = () => {
            if (sel.value) {
                flagActive(sel);
                bringFile('crime/caste/detenues_caste_analysis/state', sel.value, 'caste');
                wipeSome('caste', ['casteDetStateTotal']);
            }
        };
    } catch (_) {}
}

async function fillPolice() {
    document.getElementById('policeDefaultBtn').onclick = async () => {
        clearDrops();
        try {
            let out = await pullJson('/api/plot/file?subpath=crime/police/police/default&file=default.csv');
            paintChart('bar', out.labels, out.values, 'Police – Summary');
            stashRecall({
                spot: 'crime/police/police/default',
                fname: 'default.csv',
                chunk: 'police',
                ctype: 'bar',
                labs: out.labels,
                vals: out.values
            });
            await revealCsvBit('crime/police/police/default', 'default.csv');
        } catch (_) {}
    };

    try {
        let lst = await pullJson('/api/list?subpath=crime/police/police/top');
        let sel = document.getElementById('policeTop');
        sel.innerHTML = '<option value="">-- top --</option>';
        lst.files.forEach(f=>{
            let o=document.createElement('option');
            o.value=f; o.textContent=f; sel.appendChild(o);
        });
        sel.onchange = () => {
            if (sel.value) {
                flagActive(sel);
                bringFile('crime/police/police/top', sel.value, 'police');
                wipeSome('police', ['policeTop']);
            }
        };
    } catch (_) {}

    try {
        let lst = await pullJson('/api/list?subpath=crime/police/police/percent');
        let sel = document.getElementById('policePercents');
        sel.innerHTML = '<option value="">-- percent --</option>';
        lst.files.forEach(f=>{
            let o=document.createElement('option');
            o.value=f; o.textContent=f; sel.appendChild(o);
        });
        sel.onchange = () => {
            if (sel.value) {
                flagActive(sel);
                bringFile('crime/police/police/percent', sel.value, 'police');
                wipeSome('police', ['policePercents']);
            }
        };
    } catch (_) {}
}

async function bringFile(pathBit, fnm, area, forceType='') {
    try {
        window.__lastr.spot = pathBit;
        window.__lastr.fname = fnm;
        window.__lastr.chunk = area;
        window.__lastr.endpoint = '';

        let u = '/api/plot/file?subpath=' + encodeURIComponent(pathBit)
              + '&file=' + encodeURIComponent(fnm)
              + (forceType ? '&chart=' + encodeURIComponent(forceType) : '');
        let pulled = await pullJson(u);

        if (pulled.error) {
            alert('Error loading file: ' + pulled.error);
            return;
        }

        let titleLabel = fnm.replace('.csv','');

        if (pulled.chartType === 'multiline' && pulled.series) {
            paintChart('multiline', pulled.labels, pulled.series, titleLabel);
            stashRecall({ ctype: 'multiline', labs: pulled.labels, blobArr: pulled.series });
        } else if (pulled.chartType === 'groupedbar' && pulled.series) {
            paintChart('groupedbar', pulled.labels, pulled.series, titleLabel);
            stashRecall({ ctype: 'groupedbar', labs: pulled.labels, blobArr: pulled.series });
        } else if (pulled.chartType === 'stackedbar' && pulled.series) {
            paintChart('stackedbar', pulled.labels, pulled.series, titleLabel);
            stashRecall({ ctype: 'stackedbar', labs: pulled.labels, blobArr: pulled.series });
        } else if (pulled.series) {
            paintChart('multiline', pulled.labels, pulled.series, titleLabel);
            stashRecall({ ctype: 'multiline', labs: pulled.labels, blobArr: pulled.series });
        } else {
            let ckind = pulled.chartType || 'bar';
            paintChart(ckind, pulled.labels, pulled.values, titleLabel);
            stashRecall({ ctype: ckind, labs: pulled.labels, vals: pulled.values });
        }

        await revealCsvBit(pathBit, fnm);
    } catch (err) {
        alert('Failed to load file: ' + err.message);
    }
}
/* LITERACY – continuing, then ROADWAYS, LABOUR, INIT – last block in the kept order 

async function fillSchools() {
    try {
        let lst = await pullJson('/api/list?subpath=education/schools/state');
        let el = document.getElementById('schoolsState');
        el.innerHTML = '<option value="">-- choose state --</option>';
        lst.files.forEach(f=>{
            let o=document.createElement('option'); o.value=f; o.textContent=f;
            el.appendChild(o);
        });
        el.onchange = () => {
            if (el.value) {
                flagActive(el);
                bringFile('education/schools/state', el.value, 'schools');
            }
        };
    } catch (_) {}

    let levRadios = document.getElementsByName('schoolLevel');
    levRadios.forEach(r => {
        r.addEventListener('change', async () => {
            let pick = document.querySelector('input[name="schoolLevel"]:checked')?.value;
            if (!pick) return;
            document.getElementById('schoolLevelControls').classList.remove('hidden');

            try {
                let bestList = await pullJson(`/api/list?subpath=education/schools/best/${pick}/best`);
                let selB = document.getElementById('schoolsBest');
                selB.innerHTML = '<option value="">-- choose --</option>';
                bestList.files.forEach(f=>{
                    let o=document.createElement('option'); o.value=f; o.textContent=f;
                    selB.appendChild(o);
                });
                selB.onchange = () => {
                    if (selB.value) {
                        flagActive(selB);
                        bringFile(`education/schools/best/${pick}/best`, selB.value, 'schools');
                    }
                };
            } catch (_) {}

            try {
                let worstList = await pullJson(`/api/list?subpath=education/schools/best/${pick}/worst`);
                let selW = document.getElementById('schoolsWorst');
                selW.innerHTML = '<option value="">-- choose --</option>';
                worstList.files.forEach(f=>{
                    let o=document.createElement('option'); o.value=f; o.textContent=f;
                    selW.appendChild(o);
                });
                selW.onchange = () => {
                    if (selW.value) {
                        flagActive(selW);
                        bringFile(`education/schools/best/${pick}/worst`, selW.value, 'schools');
                    }
                };
            } catch (_) {}
        });
    });
}

async function fillLogistics() {
    let btn1 = document.getElementById('logisticsToiletBtn');
    let btn2 = document.getElementById('logisticsGirlsToiletBtn');
    let btn3 = document.getElementById('logisticsComputerBtn');

    btn1.onclick = async () => {
        try {
            let out = await pullJson('/api/plot/file?subpath=education/logistics/toilet&file=summary.csv');
            paintChart('bar', out.labels, out.values, 'Toilets');
            stashRecall({ spot:'education/logistics/toilet', fname:'summary.csv', chunk:'logistics', ctype:'bar', labs:out.labels, vals:out.values });
            await revealCsvBit('education/logistics/toilet','summary.csv');
        } catch (_) {}
    };

    btn2.onclick = async () => {
        try {
            let out = await pullJson('/api/plot/file?subpath=education/logistics/girls_toilet&file=summary.csv');
            paintChart('bar', out.labels, out.values, 'Girls Toilet');
            stashRecall({ spot:'education/logistics/girls_toilet', fname:'summary.csv', chunk:'logistics', ctype:'bar', labs:out.labels, vals:out.values });
            await revealCsvBit('education/logistics/girls_toilet','summary.csv');
        } catch (_) {}
    };

    btn3.onclick = async () => {
        try {
            let out = await pullJson('/api/plot/file?subpath=education/logistics/computer&file=summary.csv');
            paintChart('bar', out.labels, out.values, 'Computers');
            stashRecall({ spot:'education/logistics/computer', fname:'summary.csv', chunk:'logistics', ctype:'bar', labs:out.labels, vals:out.values });
            await revealCsvBit('education/logistics/computer','summary.csv');
        } catch (_) {}
    };
}

async function fillRates() {
    let rateRad = document.getElementsByName('rateType');
    rateRad.forEach(r => {
        r.addEventListener('change', () => {
            let val = document.querySelector('input[name="rateType"]:checked')?.value;

            document.getElementById('dropoutControls').classList.add('hidden');
            document.getElementById('literacyRateControls').classList.add('hidden');
            document.getElementById('yearSchoolControls').classList.add('hidden');

            if (val === 'dropout') {
                document.getElementById('dropoutControls').classList.remove('hidden');
            } else if (val === 'literacy') {
                document.getElementById('literacyRateControls').classList.remove('hidden');
            } else if (val === 'yearschool') {
                document.getElementById('yearSchoolControls').classList.remove('hidden');
            }
        });
    });

    let dropMain = document.getElementById('dropoutCategory');
    dropMain.onchange = async function () {
        let cat = dropMain.value;
        if (!cat) {
            document.getElementById('dropoutSubControls').classList.add('hidden');
            return;
        }
        document.getElementById('dropoutSubControls').classList.remove('hidden');
        let subSel = document.getElementById('dropoutSubSelect');

        let p = '';
        if (cat === 'state_level') p = 'education/rate/dropout/state_level';
        else if (cat === 'state_gender') p = 'education/rate/dropout/state_gender';
        else if (cat === 'level_gender') p = 'education/rate/dropout/level_gender';

        try {
            let listing = await pullJson(`/api/list?subpath=${p}`);
            subSel.innerHTML = '<option value="">-- choose --</option>';
            (listing.dirs || []).forEach(d => {
                let o=document.createElement('option'); o.value=d; o.textContent=d;
                subSel.appendChild(o);
            });

            subSel.onchange = async function () {
                if (!this.value) return;
                let full = `${p}/${this.value}`;
                try {
                    let files = await pullJson(`/api/list?subpath=${full}`);
                    if (files.files && files.files.length > 0) {
                        flagActive(subSel);
                        bringFile(full, files.files[0], 'rates');
                    }
                } catch (_) {}
            };

        } catch (_) {}
    };

    try {
        let lt = await pullJson('/api/list?subpath=education/rate/rate/top');
        let el = document.getElementById('literacyTop');
        el.innerHTML = '<option value="">-- choose --</option>';
        lt.files.forEach(f=>{
            let o=document.createElement('option'); o.value=f; o.textContent=f;
            el.appendChild(o);
        });
        el.onchange = ()=>{ if(el.value){ flagActive(el); bringFile('education/rate/rate/top', el.value, 'rates'); } };
    } catch (_) {}

    try {
        let lb = await pullJson('/api/list?subpath=education/rate/rate/bottom');
        let el = document.getElementById('literacyBottom');
        el.innerHTML = '<option value="">-- choose --</option>';
        lb.files.forEach(f=>{
            let o=document.createElement('option'); o.value=f; o.textContent=f;
            el.appendChild(o);
        });
        el.onchange = ()=>{ if(el.value){ flagActive(el); bringFile('education/rate/rate/bottom', el.value, 'rates'); } };
    } catch (_) {}

    try {
        let ls = await pullJson('/api/list?subpath=education/rate/rate/state_outputs');
        let el = document.getElementById('literacyState');
        el.innerHTML = '<option value="">-- choose state --</option>';
        ls.files.forEach(f=>{
            let o=document.createElement('option'); o.value=f; o.textContent=f;
            el.appendChild(o);
        });
        el.onchange = ()=>{ if(el.value){ flagActive(el); bringFile('education/rate/rate/state_outputs', el.value, 'rates'); } };
    } catch (_) {}

    try {
        let yt = await pullJson('/api/list?subpath=education/rate/year_of_school/top');
        let el = document.getElementById('yearSchoolTop');
        el.innerHTML = '<option value="">-- choose --</option>';
        yt.files.forEach(f=>{
            let o=document.createElement('option'); o.value=f; o.textContent=f;
            el.appendChild(o);
        });
        el.onchange = ()=>{ if(el.value){ flagActive(el); bringFile('education/rate/year_of_school/top', el.value, 'rates'); } };
    } catch (_) {}

    try {
        let yb = await pullJson('/api/list?subpath=education/rate/year_of_school/bottom');
        let el = document.getElementById('yearSchoolBottom');
        el.innerHTML = '<option value="">-- choose --</option>';
        yb.files.forEach(f=>{
            let o=document.createElement('option'); o.value=f; o.textContent=f;
            el.appendChild(o);
        });
        el.onchange = ()=>{ if(el.value){ flagActive(el); bringFile('education/rate/year_of_school/bottom', el.value, 'rates'); } };
    } catch (_) {}

    try {
        let ys = await pullJson('/api/list?subpath=education/rate/year_of_school/statewise_outputs');
        let el = document.getElementById('yearSchoolState');
        el.innerHTML = '<option value="">-- choose state --</option>';
        ys.files.forEach(f=>{
            let o=document.createElement('option'); o.value=f; o.textContent=f;
            el.appendChild(o);
        });
        el.onchange = ()=>{ if(el.value){ flagActive(el); bringFile('education/rate/year_of_school/statewise_outputs', el.value, 'rates'); } };
    } catch (_) {}
}

async function fillRoadways() {
    document.getElementById('roadwaysTop10Btn').onclick = async () => {
        try {
            let out = await pullJson('/api/plot/file?subpath=infrastructure/best&file=top10_ratio_states.csv');
            if (out.chartType === 'multiline') {
                paintChart('multiline', out.labels, out.series, 'Top 10 States');
                stashRecall({ spot:'infrastructure/best', fname:'top10_ratio_states.csv', chunk:'roadways', ctype:'multiline', labs:out.labels, blobArr:out.series });
                await revealCsvBit('infrastructure/best','top10_ratio_states.csv');
            }
        } catch (_) {}
    };

    document.getElementById('roadwaysBottom10Btn').onclick = async () => {
        try {
            let out = await pullJson('/api/plot/file?subpath=infrastructure/worst&file=bottom10_ratio_states.csv');
            if (out.chartType === 'multiline') {
                paintChart('multiline', out.labels, out.series, 'Bottom 10 States');
                stashRecall({ spot:'infrastructure/worst', fname:'bottom10_ratio_states.csv', chunk:'roadways', ctype:'multiline', labs:out.labels, blobArr:out.series });
                await revealCsvBit('infrastructure/worst','bottom10_ratio_states.csv');
            }
        } catch (_) {}
    };

    try {
        let lst = await pullJson('/api/list?subpath=infrastructure/surface');
        let el = document.getElementById('roadwaysStateWise');
        el.innerHTML = '<option value="">-- pick state file --</option>';
        lst.files.forEach(f=>{
            let o=document.createElement('option'); o.value=f; o.textContent=f;
            el.appendChild(o);
        });
        el.onchange = ()=>{ if(el.value){ flagActive(el); bringFile('infrastructure/surface', el.value, 'roadways'); } };
    } catch (_) {}

    try {
        let lst = await pullJson('/api/list?subpath=infrastructure/ratio');
        let el = document.getElementById('roadwaysStateRatio');
        el.innerHTML = '<option value="">-- pick ratio file --</option>';
        lst.files.forEach(f=>{
            let o=document.createElement('option'); o.value=f; o.textContent=f;
            el.appendChild(o);
        });
        el.onchange = ()=>{ if(el.value){ flagActive(el); bringFile('infrastructure/ratio', el.value, 'roadways'); } };
    } catch (_) {}
}

async function fillLabour() {
    document.getElementById('jobSeekersAllBtn').onclick = async () => {
        try {
            let out = await pullJson('/api/plot/file?subpath=employment/state/jobseeker/default&file=statewise.csv');
            paintChart(out.chartType || 'bar', out.labels, out.values, 'All States – Job Seekers');
            stashRecall({ spot:'employment/state/jobseeker/default', fname:'statewise.csv', chunk:'jobSeekers', ctype:out.chartType || 'bar', labs:out.labels, vals:out.values });
            await revealCsvBit('employment/state/jobseeker/default','statewise.csv');
        } catch (_) {}
    };

    document.getElementById('jobSeekersBottom20Btn').onclick = async () => {
        try {
            let out = await pullJson('/api/plot/file?subpath=employment/state/jobseeker/bottom&file=bottom20.csv');
            paintChart(out.chartType || 'bar', out.labels, out.values, 'Bottom 20 States – Job Seekers');
            stashRecall({ spot:'employment/state/jobseeker/bottom', fname:'bottom20.csv', chunk:'jobSeekers', ctype:out.chartType || 'bar', labs:out.labels, vals:out.values });
            await revealCsvBit('employment/state/jobseeker/bottom','bottom20.csv');
        } catch (_) {}
    };

    document.getElementById('jobSeekersTop20Btn').onclick = async () => {
        try {
            let out = await pullJson('/api/plot/file?subpath=employment/state/jobseeker/top&file=top10.csv');
            paintChart(out.chartType || 'bar', out.labels, out.values, 'Top States – Job Seekers');
            stashRecall({ spot:'employment/state/jobseeker/top', fname:'top10.csv', chunk:'jobSeekers', ctype:out.chartType || 'bar', labs:out.labels, vals:out.values });
            await revealCsvBit('employment/state/jobseeker/top','top10.csv');
        } catch (_) {}
    };

    try {
        let lst = await pullJson('/api/list?subpath=employment/state/jobseeker/statewise');
        let el = document.getElementById('jobSeekersStateWise');
        el.innerHTML = '<option value="">-- pick state file --</option>';
        lst.files.forEach(f=>{
            let o=document.createElement('option'); o.value=f; o.textContent=f;
            el.appendChild(o);
        });
        el.onchange = ()=>{ if(el.value){ flagActive(el); bringFile('employment/state/jobseeker/statewise', el.value, 'jobSeekers'); } };
    } catch (_) {}

    document.getElementById('registeredStatewiseBtn').onclick = async () => {
        try {
            let out = await pullJson('/api/plot/file?subpath=employment/state/registered_statewise&file=statewise_registration_percentage.csv');
            paintChart(out.chartType || 'bar', out.labels, out.values, 'Statewise Registration');
            stashRecall({ spot:'employment/state/registered_statewise', fname:'statewise_registration_percentage.csv', chunk:'registered', ctype:out.chartType || 'bar', labs:out.labels, vals:out.values });
            await revealCsvBit('employment/state/registered_statewise','statewise_registration_percentage.csv');
        } catch (_) {}
    };

    document.getElementById('occupationBtn').onclick = async () => {
        try {
            let out = await pullJson('/api/plot/file?subpath=employment/occupation&file=registration.csv');
            paintChart(out.chartType || 'bar', out.labels, out.values, 'Occupation');
            stashRecall({ spot:'employment/occupation', fname:'registration.csv', chunk:'occupation', ctype:out.chartType || 'bar', labs:out.labels, vals:out.values });
            await revealCsvBit('employment/occupation','registration.csv');
        } catch (_) {}
    };

    document.getElementById('ageBtn').onclick = async () => {
        try {
            let out = await pullJson('/api/plot/file?subpath=employment/agegender/age&file=ageseek.csv');
            paintChart(out.chartType || 'bar', out.labels, out.values, 'Age');
            stashRecall({ spot:'employment/agegender/age', fname:'ageseek.csv', chunk:'ageGender', ctype:out.chartType || 'bar', labs:out.labels, vals:out.values });
            await revealCsvBit('employment/agegender/age','ageseek.csv');
        } catch (_) {}
    };

    document.getElementById('genderBtn').onclick = async () => {
        try {
            let out = await pullJson('/api/plot/file?subpath=employment/agegender/gender_reg&file=genderwise_registered.csv');
            paintChart(out.chartType || 'pie', out.labels, out.values, 'Gender');
            stashRecall({ spot:'employment/agegender/gender_reg', fname:'genderwise_registered.csv', chunk:'ageGender', ctype:out.chartType || 'pie', labs:out.labels, vals:out.values });
            await revealCsvBit('employment/agegender/gender_reg','genderwise_registered.csv');
        } catch (_) {}
    };
}

/* INIT 

document.addEventListener('DOMContentLoaded', () => {
    let toggle = document.getElementById('valueToggle');
    toggle.addEventListener('change', () => {
        window.__showV = toggle.checked;
        if (window.__cinst) {
            let t = window.__cinst.config.type;
            let labs = window.__cinst.data.labels || [];
            let ds = window.__cinst.data.datasets;
            if (ds.length > 1) {
                let bunch = ds.map(d => ({ label:d.label, data:d.data }));
                paintChart('multiline', labs, bunch, ds[0].label || '');
            } else {
                let d = ds[0].data;
                paintChart(t, labs, d, ds[0].label || '');
            }
        }
    });

    let barBtn = document.getElementById('barBtn');
    let pieBtn = document.getElementById('pieBtn');
    if (barBtn && pieBtn) {
        barBtn.addEventListener('click', () => twistChart('bar'));
        pieBtn.addEventListener('click', () => twistChart('pie'));
    }
});

window.addEventListener('load', async () => {
    document.getElementById('btnMainCrime').onclick = () => pickMain('crime');
    document.getElementById('btnMainLiteracy').onclick = () => pickMain('literacy');
    document.getElementById('btnMainRoadways').onclick = () => pickMain('roadways');
    document.getElementById('btnMainLabour').onclick = () => pickMain('labour');

    document.getElementById('btnTotal').onclick = () => pickArea('total');
    document.getElementById('btnReligion').onclick = () => pickArea('religion');
    document.getElementById('btnWomen').onclick = () => pickArea('women');
    document.getElementById('btnEducation').onclick = () => pickArea('education');
    document.getElementById('btnCaste').onclick = () => pickArea('caste');
    document.getElementById('btnPolice').onclick = () => pickArea('police');
    document.getElementById('btnChildren').onclick = () => pickArea('children');

    document.getElementById('btnSchools').onclick = () => pickEdu('schools');
    document.getElementById('btnLogistics').onclick = () => pickEdu('logistics');
    document.getElementById('btnRates').onclick = () => pickEdu('rates');

    document.getElementById('btnStatewise').onclick = () => pickLab('statewise');
    document.getElementById('btnOccupation').onclick = () => pickLab('occupation');
    document.getElementById('btnAgeGender').onclick = () => pickLab('ageGender');

    document.getElementById('btnJobSeekers').onclick = () => pickLabSub('jobSeekers');
    document.getElementById('btnRegistered').onclick = () => pickLabSub('registered');

    try { await fillTotals(); } catch (_) {}
    try { await fillReligion(); } catch (_) {}
    try { await fillWomen(); } catch (_) {}
    try { await fillEduCrime(); } catch (_) {}
    try { await fillCaste(); } catch (_) {}
    try { await fillPolice(); } catch (_) {}
    try { await fillChildren(); } catch (_) {}

    try { await fillSchools(); } catch (_) {}
    try { await fillLogistics(); } catch (_) {}
    try { await fillRates(); } catch (_) {}

    try { await fillRoadways(); } catch (_) {}
    try { await fillLabour(); } catch (_) {}
});
