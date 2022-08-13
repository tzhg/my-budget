/* global $ */

"use strict";

import Data from "./data.json";
import "./style.css";

$(() => {

const NS = "http://www.w3.org/2000/svg";

const config = Data.config;
const info = Data.info;
const data = Data.data;

const m = data.cash[2].length;

const chartWidth = 260;
const rowHeight = 21;

const intraPad = 1;

const dataInfo = {
    "cash": {
        "label": "Cash",
        "colour": "#cbcc64",
        "chart": 0
    },
    "financial": {
        "label": "Financial assets",
        "colour": "#af9a40",
        "chart": 0
    },
    "real": {
        "label": "Real assets",
        "colour": "#765128",
        "chart": 0
    },
    "debt": {
        "label": "Debt",
        "colour": "#c14c89",
        "chart": 0
    },
    "income": {
        "label": "Income",
        "colour": "#5da145",
        "chart": 1
    },
    "expenses": {
        "label": "Expenses",
        "colour": "#b85447",
        "chart": 1
    },
    "profit": {
        "label": "Savings profit",
        "colour": "#366a24",
        "chart": 1
    },
    "loss": {
        "label": "Savings loss",
        "colour": "#76332a",
        "chart": 1
    },
    "housing": {
        "label": "Housing",
        "colour": "#92ddd1",
        "chart": 2
    },
    "food": {
        "label": "Food",
        "colour": "#586abf",
        "chart": 2
    },
    "shopping": {
        "label": "Shopping",
        "colour": "#bc98d9",
        "chart": 2
    },
    "utilities": {
        "label": "Utilities",
        "colour": "#68aecc",
        "chart": 2
    },
    "health": {
        "label": "Health",
        "colour": "#261a3d",
        "chart": 2
    },
    "leisure": {
        "label": "Leisure",
        "colour": "#994cb9",
        "chart": 2
    }
}

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
        config.gridlines[0][config.gridlines[0].length - 1],
        config.gridlines[1][config.gridlines[1].length - 1],
        config.gridlines[2][config.gridlines[2].length - 1]
    ];

    return 100 * val / max_val[chart];
};

const dataPx = Object.fromEntries(
    Object.entries(dataInfo).map(
        ([key, info], j) => [key, data[key].map(arr2 => arr2.map(val => getWidth(val, info.chart)))]
    )
);

/* Returns month and year n months before current month */
const getDate = (n) => {
    const month = info.startDate[0] - 1 + m - n;

    return [month % 12, info.startDate[1] + Math.floor(month / 12)];
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
    /* Sets title */
    $(".title-date > span").text(`${monthNames[info.endDate[0] - 1]}\xa0${info.endDate[1]}`);

    for (let [key, value] of Object.entries(data)) {
        if (key === "netAssets") {
            $(`.head-net-assets > .val`).text(formatVal(value[0][0]));
        } else if (key === "netIncome") {
            $(`.head-net-income > .val`).text(formatVal(value[0][0]));
        } else {
            $(`.val-${key}`).text(formatVal(value[0][0]));
        }
    }
};

const drawChartBar = (chart, a, b, $dest) => {
    const barHeight = (rowHeight - intraPad) / 2;

    if (chart === 0) {
        const $rect0 = $(document.createElement("div"))
        const $rect1 = $(document.createElement("div"))
        const $rect2 = $(document.createElement("div"))
        const $rect3 = $(document.createElement("div"))

        $rect0.addClass("chart-rect");
        $rect1.addClass("chart-rect");
        $rect2.addClass("chart-rect");
        $rect3.addClass("chart-rect");

        $rect0.attr("data-rect", `cash-${a}-${b}`);
        $rect1.attr("data-rect", `financial-${a}-${b}`);
        $rect2.attr("data-rect", `real-${a}-${b}`);
        $rect3.attr("data-rect", `debt-${a}-${b}`);

        $rect0.css({
            "background-color": dataInfo.cash.colour,
            "width": `${dataPx.cash[a][b]}%`,
            "height": `${barHeight}px`,
            "left": 0,
            "top": 0
        });
        $rect1.css({
            "background-color": dataInfo.financial.colour,
            "width": `${dataPx.financial[a][b]}%`,
            "height": `${barHeight}px`,
            "left": `${dataPx.cash[a][b]}%`,
            "top": 0
        });
        $rect2.css({
            "background-color": dataInfo.real.colour,
            "width": `${dataPx.real[a][b]}%`,
            "height": `${barHeight}px`,
            "left": `${dataPx.cash[a][b] + dataPx.financial[a][b]}%`,
            "top": 0
        });
        $rect3.css({
            "background-color": dataInfo.debt.colour,
            "width": `${dataPx.debt[a][b]}%`,
            "height": `${barHeight}px`,
            "left": 0,
            "top": `${barHeight + intraPad}px`
        });

        $dest
            .append($rect0)
            .append($rect1)
            .append($rect2)
            .append($rect3);
    } else if (chart === 1) {
        const $rect0 = $(document.createElement("div"))
        const $rect1 = $(document.createElement("div"))
        const $rect2 = $(document.createElement("div"))
        const $rect3 = $(document.createElement("div"))

        $rect0.addClass("chart-rect");
        $rect1.addClass("chart-rect");
        $rect2.addClass("chart-rect");
        $rect3.addClass("chart-rect");

        $rect0.attr("data-rect", `expenses-${a}-${b}`);
        $rect1.attr("data-rect", `income-${a}-${b}`);
        $rect2.attr("data-rect", `loss-${a}-${b}`);
        $rect3.attr("data-rect", `profit-${a}-${b}`);

        $rect0.css({
            "background-color": dataInfo.expenses.colour,
            "width": `${dataPx.expenses[a][b]}%`,
            "height": `${barHeight}px`,
            "left": 0,
            "top": `${barHeight + intraPad}px`
        });
        $rect1.css({
            "background-color": dataInfo.income.colour,
            "width": `${dataPx.income[a][b]}%`,
            "height": `${barHeight}px`,
            "left": 0,
            "top": 0
        });
        $rect2.css({
            "background-color": dataInfo.loss.colour,
            "width": `${dataPx.loss[a][b]}%`,
            "height": `${barHeight}px`,
            "left": `${dataPx.expenses[a][b]}%`,
            "top": `${barHeight + intraPad}px`
        });
        $rect3.css({
            "background-color": dataInfo.profit.colour,
            "width": `${dataPx.profit[a][b]}%`,
            "height": `${barHeight}px`,
            "left": `${dataPx.income[a][b]}%`,
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

        $rect0.attr("data-rect", `housing-${a}-${b}`);
        $rect1.attr("data-rect", `food-${a}-${b}`);
        $rect2.attr("data-rect", `shopping-${a}-${b}`);
        $rect3.attr("data-rect", `utilities-${a}-${b}`);
        $rect4.attr("data-rect", `health-${a}-${b}`);
        $rect5.attr("data-rect", `leisure-${a}-${b}`);

        $rect0.css({
            "background-color": dataInfo.housing.colour,
            "width": `${dataPx.housing[a][b]}%`,
            "height": `${barHeight}px`,
            "left": 0,
            "top": 0
        });
        $rect1.css({
            "background-color": dataInfo.food.colour,
            "width": `${dataPx.food[a][b]}%`,
            "height": `${barHeight}px`,
            "left": `${dataPx.housing[a][b] + dataPx.utilities[a][b]}%`,
            "top": 0
        });
        $rect2.css({
            "background-color": dataInfo.shopping.colour,
            "width": `${dataPx.shopping[a][b]}%`,
            "height": `${barHeight}px`,
            "left": 0,
            "top": `${barHeight + intraPad}px`
        });
        $rect3.css({
            "background-color": dataInfo.utilities.colour,
            "width": `${dataPx.utilities[a][b]}%`,
            "height": `${barHeight}px`,
            "left": `${dataPx.housing[a][b]}%`,
            "top": 0
        });
        $rect4.css({
            "background-color": dataInfo.health.colour,
            "width": `${dataPx.health[a][b]}%`,
            "height": `${barHeight}px`,
            "left": `${dataPx.housing[a][b] + dataPx.utilities[a][b] + dataPx.food[a][b]}%`,
            "top": 0
        });
        $rect5.css({
            "background-color": dataInfo.leisure.colour,
            "width": `${dataPx.leisure[a][b]}%`,
            "height": `${barHeight}px`,
            "left": `${dataPx.shopping[a][b]}%`,
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
    let title;
    if (a === 0) {
        dateText = "MTD";
        title = "Month to date";
    } else if (a === 1) {
        dateText = "12M\xa0avg";
        title = "12-month\xa0average";
    } else if (a === 2) {
        dateText = `${monthNames[getDate(b + 1)[0]].slice(0, 3)}`;
    }

    $text.prop("title", title);

    $text.text(dateText);

    $dest.append($text);

    $text.css({
        "top": `calc(50% - ${$text.height() / 2}px)`
    });
};

const gridLines = (i, $dest) => {
    config.gridlines[i].forEach((val, k) => {
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
                "left": `${1 - $gridLabel.width() / 2}px`
            });
        } else {
            $gridLine.addClass("grid-line");
            $gridLine.css({
                "left": `calc(${getWidth(val, i)}% - 1px)`
            });
            $gridLabel.css({
                "left": `calc(${getWidth(val, i)}% - ${$gridLabel.width() / 2}px)`
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

            $(`.body-${i}`)
                .append($yearRow)
                .append($chartContainer);
            $chartContainer.append($chart);

            gridLines(i, $chartContainer);

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
            const rect = elem.dataset.rect.split("-");
            rect[1] = Number(rect[1]);
            rect[2] = Number(rect[2]);

            let label1;
            if (rect[1] === 0) {
                label1 = "Month to date";
            } else if (rect[1] === 1) {
                label1 = "12-month\xa0average";
            } else if (rect[1] === 2) {
                let date = getDate(rect[2] + 1);
                label1 = `${monthNames[date[0]]}\xa0${date[1]}`;
            }

            const value = formatVal(data[rect[0]][rect[1]][rect[2]]);
            const label2 = `${dataInfo[rect[0]].label}: ${value}`;

            let label3;
            if (dataInfo[rect[0]].chart === 0) {
                label3 = `Net assets: ${formatVal(data.netAssets[rect[1]][rect[2]])}`;
            } else if (dataInfo[rect[0]].chart === 1) {
                label3 = `Net income: ${formatVal(data.netIncome[rect[1]][rect[2]])}`;
            }

            $(".tooltip").show();
            const $ttElem = $(".tooltip");
            $ttElem.empty();

            let $ttContent = $(document.createElement("div"));
            let $label1 = $(document.createElement("div"));
            let $label2 = $(document.createElement("div"));
            let $label3 = $(document.createElement("div"));

            $label1.addClass("tt-1");
            $label2.addClass("tt-2");
            $label3.addClass("tt-3");

            $label1.text(label1);
            $label2.text(label2);
            $label3.text(label3);

            $ttContent.append($label1);
            $ttContent.append($label2);
            $ttContent.append($label3);

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
