/* global $ */

"use strict";

import { importData } from "./importData.js";

$(() => {

const NS = "http://www.w3.org/2000/svg";

const dataImp = importData();

const para = dataImp.para;
const info = dataImp.info;
const data = dataImp.data;

const m = data[0][2].length;

const chartWidth = 260;
const rowHeight = 19;

const intraPad = 1;

const labels = [
    "Cash",
    "Savings",
    "Debt",
    "Income",
    "Expenses",
    "Profit",
    "Loss",
    "Housing",
    "Food",
    "Durable",
    "Utilities",
    "Health",
    "Leisure"
];

const pal = [
    "#edc948",
    "#bab0ac",
    "#5a5f68",
    "#59a14f",
    "#e15759",
    "#3e7137",
    "#b92123",
    "#4e79a7",
    "#b07aa1",
    "#9c755f",
    "#76b7b2",
    "#ff9da7",
    "#f28e2b"
];

const scale = [0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2];

const formatVal = (value, style="default") => {
    /* https://stackoverflow.com/a/2901298 */
    function numberWithCommas(x) {
        return x.toString().replace(/\B(?<!\.\d*)(?=(\d{3})+(?!\d))/g, ",");
    }

    if (value === 0) {
        return "0";
    }

    if (style === "default") {
        value = value.toFixed(0);
    } else if (style === "short") {
        value = value.toFixed(0);
    }
    return numberWithCommas(value);
};

const getWidth = (val, chart) => {
    const max_val = [
        para.gridlines[0][para.gridlines[0].length - 1],
        para.gridlines[1][para.gridlines[1].length - 1],
        para.gridlines[2][para.gridlines[2].length - 1]
    ];

    return 100 * val / max_val[chart];
};

/* Bar widths in each chart */
const dataPx = [
    data.map((arr, i) => arr[0].map(val => getWidth(val, scale[i]))),
    data.map((arr, i) => arr[1].map(val => getWidth(val, scale[i]))),
    data.map((arr, i) => arr[2].map(val => getWidth(val, scale[i])))
];

/* Returns month and year n months before current month */
const getDate = (n) => {
    const month = info.startDate[1] - 1 + m - n;

    return [month % 12, info.startDate[2] + Math.floor(month / 12)];
};

const monthNames = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
];

const getTimeLabel = (chart, n, style) => {
    if (chart === 0) {
        let date = getDate(0);
        if (style === "short") {
            date[0] = monthNames[date[0]].slice(0, 3);
        }
        return `${date[0]}\xa0${date[1]}`;
    } else if (chart === 1) {
        if (style === "short") {
            return "12m\xa0average";
        }
        return "12-month\xa0average";
    } else if (chart === 2) {
        let date = getDate(n + 1);
        if (style === "short") {
            date[0] = monthNames[date[0]].slice(0, 3);
        }
        return `${date[0]}\xa0${date[1]}`;
    }
};

const updateLegend = () => {
    for (let i = 0; i < 13; ++i) {
        $(`.val-${i}`).text(formatVal(data[i][0][0]));
    }
};

const drawChartBar = (chart, a, b, $dest) => {
    const barHeight = (rowHeight - intraPad) / 2;

    if (chart === 0) {
        const $rect0 = $(document.createElement("div"))
        const $rect1 = $(document.createElement("div"))
        const $rect2 = $(document.createElement("div"))

        $rect0.addClass("chart-rect");
        $rect1.addClass("chart-rect");
        $rect2.addClass("chart-rect");

        $rect0.attr("data-rect", `0-${a}-${b}`);
        $rect1.attr("data-rect", `1-${a}-${b}`);
        $rect2.attr("data-rect", `2-${a}-${b}`);

        $rect0.css({
            "background-color": pal[0],
            "width": `${dataPx[a][0][b]}%`,
            "height": `${barHeight}px`,
            "left": 0,
            "top": 0
        });
        $rect1.css({
            "background-color": pal[1],
            "width": `${dataPx[a][1][b]}%`,
            "height": `${barHeight}px`,
            "left": `${dataPx[a][0][b]}%`,
            "top": 0
        });
        $rect2.css({
            "background-color": pal[2],
            "width": `${dataPx[a][2][b]}%`,
            "height": `${barHeight}px`,
            "left": 0,
            "top": `${barHeight + intraPad}px`
        });

        $dest
            .append($rect0)
            .append($rect1)
            .append($rect2);
    } else if (chart === 1) {
        const $rect0 = $(document.createElement("div"))
        const $rect1 = $(document.createElement("div"))
        const $rect2 = $(document.createElement("div"))
        const $rect3 = $(document.createElement("div"))

        $rect0.addClass("chart-rect");
        $rect1.addClass("chart-rect");
        $rect2.addClass("chart-rect");
        $rect3.addClass("chart-rect");

        $rect0.attr("data-rect", `4-${a}-${b}`);
        $rect1.attr("data-rect", `3-${a}-${b}`);
        $rect2.attr("data-rect", `6-${a}-${b}`);
        $rect3.attr("data-rect", `5-${a}-${b}`);

        $rect0.css({
            "background-color": pal[4],
            "width": `${dataPx[a][4][b]}%`,
            "height": `${barHeight}px`,
            "left": 0,
            "top": `${barHeight + intraPad}px`
        });
        $rect1.css({
            "background-color": pal[3],
            "width": `${dataPx[a][3][b]}%`,
            "height": `${barHeight}px`,
            "left": 0,
            "top": 0
        });
        $rect2.css({
            "background-color": pal[6],
            "width": `${dataPx[a][6][b]}%`,
            "height": `${barHeight}px`,
            "left": `${dataPx[a][4][b]}%`,
            "top": `${barHeight + intraPad}px`
        });
        $rect3.css({
            "background-color": pal[5],
            "width": `${dataPx[a][5][b]}%`,
            "height": `${barHeight}px`,
            "left": `${dataPx[a][3][b]}%`,
            "top": 0
        });

        $dest
            .append($rect0)
            .append($rect1)
            .append($rect2)
            .append($rect3);
    } else if (chart === 2) {
        const $rect0 = $(document.createElement("div"))
        const $rect1 = $(document.createElement("div"))
        const $rect2 = $(document.createElement("div"))
        const $rect3 = $(document.createElement("div"))
        const $rect4 = $(document.createElement("div"))
        const $rect5 = $(document.createElement("div"))

        $rect0.addClass("chart-rect");
        $rect1.addClass("chart-rect");
        $rect2.addClass("chart-rect");
        $rect3.addClass("chart-rect");
        $rect4.addClass("chart-rect");
        $rect5.addClass("chart-rect");

        $rect0.attr("data-rect", `7-${a}-${b}`);
        $rect1.attr("data-rect", `8-${a}-${b}`);
        $rect2.attr("data-rect", `9-${a}-${b}`);
        $rect3.attr("data-rect", `10-${a}-${b}`);
        $rect4.attr("data-rect", `11-${a}-${b}`);
        $rect5.attr("data-rect", `12-${a}-${b}`);

        $rect0.css({
            "background-color": pal[7],
            "width": `${dataPx[a][7][b]}%`,
            "height": `${barHeight}px`,
            "left": 0,
            "top": 0
        });
        $rect1.css({
            "background-color": pal[8],
            "width": `${dataPx[a][8][b]}%`,
            "height": `${barHeight}px`,
            "left": `${dataPx[a][7][b] + dataPx[a][10][b]}%`,
            "top": 0
        });
        $rect2.css({
            "background-color": pal[9],
            "width": `${dataPx[a][9][b]}%`,
            "height": `${barHeight}px`,
            "left": 0,
            "top": `${barHeight + intraPad}px`
        });
        $rect3.css({
            "background-color": pal[10],
            "width": `${dataPx[a][10][b]}%`,
            "height": `${barHeight}px`,
            "left": `${dataPx[a][7][b]}%`,
            "top": 0
        });
        $rect4.css({
            "background-color": pal[11],
            "width": `${dataPx[a][11][b]}%`,
            "height": `${barHeight}px`,
            "left": `${dataPx[a][7][b] + dataPx[a][10][b] + dataPx[a][8][b]}%`,
            "top": 0
        });
        $rect5.css({
            "background-color": pal[12],
            "width": `${dataPx[a][12][b]}%`,
            "height": `${barHeight}px`,
            "left": `${dataPx[a][9][b]}%`,
            "top": `${barHeight + intraPad}px`
        });

        $dest
            .append($rect0)
            .append($rect1)
            .append($rect2)
            .append($rect3)
            .append($rect4)
            .append($rect5);
    }

    const $text = $(document.createElement("div"))

    $text.addClass("time-axis-label");

    let dateText;
    if (a === 0) {
        dateText = "MTD";
    } else if (a === 1) {
        dateText = "12M\xa0avg";
    } else if (a === 2) {
        dateText = `${monthNames[getDate(b + 1)[0]].slice(0, 3)}`;
    }

    $text.text(dateText);

    $dest.append($text);

    $text.css({
        "top": `calc(50% - ${$text.height() / 2}px)`
    });
};

const gridLines = (i, $dest) => {
    para.gridlines[i].forEach((val, k) => {
        const $gridLine = $(document.createElement("div"))
        const $gridLabel = $(document.createElement("div"))

        $gridLabel.addClass("grid-label");
        $gridLabel.text(formatVal(val, "short"));

        $dest
            .append($gridLine)
            .append($gridLabel);

        if (k === 0) {
            $gridLine.addClass("grid-line-first");
            $gridLabel.css({
                "left": `${-2 - $gridLabel.width() / 2}px`
            });
        } else {
            $gridLine.addClass("grid-line");
            $gridLine.css({
                "left": `calc(${getWidth(val, i)}% - 1px)`
            });
            $gridLabel.css({
                "left": `calc(${getWidth(val, i)}% + ${-1 - $gridLabel.width() / 2}px)`
            });
        }
    });
}

const drawCharts = () => {
    const dateIndices = [];

    for (let i = 0; i < m; ++i) {
        if (i === 0 || getDate(i + 1)[0] === 11) {
            dateIndices.push([]);
        }
        dateIndices[dateIndices.length - 1].push(i);
    }

    for (let i = 0; i < 3; ++i) {
        /* Head */
        const $row0 = $(document.createElement("div"));
        const $row1 = $(document.createElement("div"));

        $(`.head-${i}2 > .chart`)
            .append($row0)
            .append($row1);

        drawChartBar(i, 0, 0, $row0);
        drawChartBar(i, 1, 0, $row1);

        const $chartContainer = $(`.head-${i}2`);
        gridLines(i, $chartContainer);

        /* Body */

        dateIndices.forEach(arr => {
            const $chart = $(document.createElement("div"));
            const $chartContainer = $(document.createElement("div"));
            const $yearRow = $(document.createElement("div"));

            $yearRow.text(getDate(arr[0] + 1)[1]);

            $chart.addClass("chart");
            $chartContainer.addClass("chart-container");
            $yearRow.addClass("year-row");

            gridLines(i, $chartContainer);

            $(`.body-${i}`)
                .append($yearRow)
                .append($chartContainer);
            $chartContainer.append($chart);

            arr.forEach(j => {
                const $row2 = $(document.createElement("div"));
                $chart.append($row2);
                drawChartBar(i, 2, j, $row2);
            });
        });
    }
};

const initTooltip = () => {
    const toolTipPosition = (x, y) => {
        const ttVSpace = 30;

        const $ttElem = $(".tooltip");

        /* Set in middle to measure width */
        $ttElem.css("left", "0");
        $ttElem.css("top", "0");

        let ttBox = $ttElem[0].getBoundingClientRect();

        const screenPad = 5;

        /* Ensures does not go off screen edge */
        x = Math.max(x, ttBox.width / 2 + screenPad);
        x = Math.min(x, $(window).width() - ttBox.width / 2 - screenPad);

        /* If too near bottom, puts tooltip above pointer */
        let dy = ttVSpace;
        if (y + ttVSpace + ttBox.height > $(window).scrollTop() + $(window).height()) {
            dy = -ttVSpace - ttBox.height;
        }

        $ttElem.css({
            "left": `${x - ttBox.width / 2}px`,
            "top": `${y + dy}px`
        });
    }

    $(document.body).on("pointerup pointermove", (evt) => {
        toolTipPosition(evt.originalEvent.pageX, evt.originalEvent.pageY);
    });

    /* sel: jQuery selector returning all buttons
    /* dataId: The buttons should have a distinct data attribute data-${id}
    /*     (non-CamelCase string)
    /* showTooltip: function (elem) */
    /* hideTooltip: function (elem) */
    const tooltip = (sel, dataId, showTooltip, hideTooltip) => {
        let toggledOnId = "";

        const toggle = (evt, on="") => {

            const id = $(evt.target).attr(`data-${dataId}`);

            /* Toggles off previous button */
            if (toggledOnId !== "") {
                const prevElem = $(`${sel}[data-${dataId}=${toggledOnId}]`)[0];
                hideTooltip(prevElem);
                $(".tooltip").hide();
            }

            if ((on === "" || on) && toggledOnId !== id) {
                /* Toggle different button */
                showTooltip(evt.target);
                toolTipPosition(evt.originalEvent.pageX, evt.originalEvent.pageY);

                $(".tooltip").show();
                toggledOnId = id;
            } else {
                /* Toggle same button */
                toggledOnId = "";
            }
        }

        $(sel)
            .on("pointerover", (evt) => {
                evt.preventDefault();

                if (evt.pointerType === "touch") {
                    toggle(evt);
                } else if (evt.pointerType !== "touch") {
                    toggle(evt, true);
                }
            })
            .on("pointerleave", (evt) => {
                evt.preventDefault();

                if (evt.pointerType !== "touch") {
                    toggle(evt, false);
                }
            });

        $(document.body).on("pointerdown pointercancel", (evt) => {
            if (evt.pointerType === "touch") {
                let id = $(evt.target).attr(`data-${dataId}`);

                /* Toggle off any buttons */
                if (toggledOnId !== id) {
                    id = toggledOnId;
                    toggle(evt, false);
                }
            }
        });
    };

    tooltip(
        ".chart-rect",
        "rect",
        (elem) => {
            let rect = elem.dataset.rect.split("-");
            rect = rect.map(x => Number(x));

            let label1;
            if (rect[1] === 0) {
                let date = getDate(0);
                label1 = `${monthNames[date[0]]}\xa0${date[1]}`;
            } else if (rect[1] === 1) {
                label1 = "12-month\xa0average";
            } else if (rect[1] === 2) {
                let date = getDate(rect[2] + 1);
                label1 = `${monthNames[date[0]]}\xa0${date[1]}`;
            }

            const value = formatVal(data[rect[0]][rect[1]][rect[2]]);
            const label2 = `${labels[rect[0]]}: ${value}`;

            $(".tooltip").show();
            const $ttElem = $(".tooltip");
            $ttElem.empty();

            let $ttContent = $(document.createElement("div"));
            let $label1 = $(document.createElement("div"));
            let $label2 = $(document.createElement("div"));

            $label1.addClass("tt-1");
            $label2.addClass("tt-2");

            $label1.text(label1);
            $label2.text(label2);

            $ttContent.append($label1);
            $ttContent.append($label2);

            $ttElem.append($ttContent);
        },
        (elem) => {
            $(".tooltip").hide();
        }
    );
};

const showTimeAxis = () => {
    $(".time-axis-label-1").show();
    $(".time-axis-label-2").show();
    if ($(window).width() >= 1250) {
        $(".time-axis-label-1").hide();
        $(".time-axis-label-2").hide();
    }
};


(() => {
    $(".title-date > span").text(`${info.endDate[0]}\xa0${monthNames[info.endDate[1] - 1]}\xa0${info.endDate[2]}`);

    updateLegend();
	drawCharts();
    initTooltip();
/*
    $(window).on("resize", () => {
        showTimeAxis();
    });
    showTimeAxis();*/
})();

});
