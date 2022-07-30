/* global $ */

"use strict";

import { importData } from "./importData.js";

$(() => {

const NS = "http://www.w3.org/2000/svg";

const dataImp = importData();

const para = dataImp.para;
const info = dataImp.info;
const data = dataImp.data;

const m = data[0].length;

const chartWidth = 260;
const rowHeight = 34;

const intraPad = 2;

const labels = [
    "Cash",
    "Savings",
    "Expenses",
    "Income",
    "Housing",
    "Food and supplies",
    "Durable goods",
    "Utilities and transport",
    "Health and beauty",
    "Leisure and hobbies",
    "Investment profit",
    "Investment loss"
];

const pal = [
    "#edc948",
    "#bab0ac",
    "#e15759",
    "#59a14f",
    "#4e79a7",
    "#b07aa1",
    "#9c755f",
    "#76b7b2",
    "#ff9da7",
    "#f28e2b",
    "#3e7137",
    "#b92123"
];

const formatVal = (value, style="default") => {
    /* https://stackoverflow.com/a/2901298 */
    function numberWithCommas(x) {
        return x.toString().replace(/\B(?<!\.\d*)(?=(\d{3})+(?!\d))/g, ",");
    }

    if (value === 0) {
        return "0";
    }

    if (style === "default") {
        value = value.toFixed(2);
    } else if (style === "short") {
        value = value.toFixed(0);
    }
    return numberWithCommas(value);
};

const getWidth = (val, type) => {
    const max_val = [
        para.gridlines[0][para.gridlines[0].length - 1],
        para.gridlines[1][para.gridlines[1].length - 1],
        para.gridlines[2][para.gridlines[2].length - 1]
    ];

    const scaleEx = [
        max_val[0],
        max_val[0],
        max_val[1],
        max_val[1],
        max_val[2],
        max_val[2],
        max_val[2],
        max_val[2],
        max_val[2],
        max_val[2],
        max_val[1],
        max_val[1]
    ];

    const w = Math.round(chartWidth * val / scaleEx[type]);

    if (w <= 2) {
        return 0;
    }
    return w;
};

const dataPx = data.map((arr, i) => arr.map(val => getWidth(val, i)));

const getDate = (month) => {
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

    const month2 = month + info.startMonth;

    return [monthNames[month2 % 12], info.startYear + Math.floor(month2 / 12)];
};

const updateLegend = () => {
    $(".val-cash").text(formatVal(data[0][0]));
    $(".val-savings").text(formatVal(data[1][0]));
    $(".val-expenses").text(formatVal(data[2][0]));
    $(".val-income").text(formatVal(data[3][0]));
    $(".val-housing").text(formatVal(data[4][0]));
    $(".val-food").text(formatVal(data[5][0]));
    $(".val-shopping").text(formatVal(data[6][0]));
    $(".val-utilities").text(formatVal(data[7][0]));
    $(".val-health").text(formatVal(data[8][0]));
    $(".val-leisure").text(formatVal(data[9][0]));
    $(".val-profit").text(formatVal(data[10][0]));
    $(".val-loss").text(formatVal(data[11][0]));
};

const drawChart0 = () => {
    para.gridlines[0].forEach((val) => {
        const $gridLabel = $(document.createElement("div"))

        $gridLabel.addClass("grid-label");
        $gridLabel.text(formatVal(val, "short"));
        $(".h0").append($gridLabel);

        $gridLabel.css({
            "left": `${getWidth(val, 0) - 1 - $gridLabel.width() / 2}px`,
        });
    });

    const $rect0 = $(document.createElement("div"))
    const $rect1 = $(document.createElement("div"))

    $rect0.addClass("chart-rect");
    $rect1.addClass("chart-rect");

    $rect0.attr("data-rect", "0-0");
    $rect1.attr("data-rect", "1-0");

    $rect0.css({
        "background-color": pal[0],
        "width": `calc(${dataPx[0][0]}px - ${dataPx[1][0] === 0 ? 0 : 0}px)`,
        "height": "100%",
        "left": 0,
        "top": 0
    });
    $rect1.css({
        "background-color": pal[1],
        "width": `${dataPx[1][0]}px`,
        "height": "100%",
        "left": `${dataPx[0][0]}px`,
        "top": 0
    });

    $(".h0 > .head-chart")
        .append($rect0)
        .append($rect1);

    para.gridlines[0].forEach((val) => {
        const $grid1 = $(document.createElement("div"))
        const $grid2 = $(document.createElement("div"))

        $grid1.addClass("grid-line");
        $grid2.addClass("grid-line");

        $grid1.css({
            "left": `calc(${getWidth(val, 0)}px - 1px)`,
        });
        $grid2.css({
            "left": `calc(${getWidth(val, 0)}px - 1px)`,
        });

        $(".h0").append($grid1);
        $(".c0").append($grid2);
    });

    for (let i = 1; i < m; ++i) {
        const $row = $(document.createElement("div"))
        const $rect0 = $(document.createElement("div"))
        const $rect1 = $(document.createElement("div"))

        $rect0.addClass("chart-rect");
        $rect1.addClass("chart-rect");

        $rect0.attr("data-rect", `0-${i}`);
        $rect1.attr("data-rect", `1-${i}`);

        $rect0.css({
            "background-color": pal[0],
            "width": `calc(${dataPx[0][i]}px - ${dataPx[1][i] === 0 ? 0 : 0}px)`,
            "height": "100%",
            "left": 0,
            "top": 0
        });
        $rect1.css({
            "background-color": pal[1],
            "width": `${dataPx[1][i]}px`,
            "height": "100%",
            "left": `${dataPx[0][i]}px`,
            "top": 0
        });

        $row
            .append($rect0)
            .append($rect1);
        $(".c0 > .long-chart").append($row);

        const $text = $(document.createElement("div"))

        $text.addClass("time-axis-label time-axis-label-0");

        const date = getDate(m - 1 - i);

        $text.text(`${date[0].slice(0, 3)} ${date[1]}`);

        $row.append($text);

        $text.css({
            "left": `${-$text.width() - 15}px`,
            "top": `calc(50% - ${$text.height() / 2}px)`
        });
    }
};

const drawChart1 = () => {
    const barHeight = (rowHeight - intraPad) / 2;

    para.gridlines[1].forEach((val) => {
        const $gridLabel = $(document.createElement("div"))

        $gridLabel.addClass("grid-label");

        $gridLabel.text(formatVal(val, "short"));

        $(".h1").append($gridLabel);

        $gridLabel.css({
            "left": `${getWidth(val, 2) - 1 - $gridLabel.width() / 2}px`
        });
    });

    const $rect0 = $(document.createElement("div"))
    const $rect1 = $(document.createElement("div"))
    const $rect2 = $(document.createElement("div"))
    const $rect3 = $(document.createElement("div"))

    $rect0.addClass("chart-rect");
    $rect1.addClass("chart-rect");
    $rect2.addClass("chart-rect");
    $rect3.addClass("chart-rect");

    $rect0.attr("data-rect", "2-0");
    $rect1.attr("data-rect", "3-0");
    $rect2.attr("data-rect", "10-0");
    $rect3.attr("data-rect", "11-0");

    $rect0.css({
        "background-color": pal[2],
        "width": `${dataPx[2][0]}px`,
        "height": `${barHeight}px`,
        "left": 0,
        "top": `${barHeight + intraPad}px`
    });
    $rect1.css({
        "background-color": pal[3],
        "width": `${dataPx[3][0]}px`,
        "height": `${barHeight}px`,
        "left": 0,
        "top": 0
    });
    $rect2.css({
        "background-color": pal[10],
        "width": `${dataPx[10][0]}px`,
        "height": `${barHeight}px`,
        "left": `${dataPx[3][0]}px`,
        "top": 0
    });
    $rect3.css({
        "background-color": pal[11],
        "width": `${dataPx[11][0]}px`,
        "height": `${barHeight}px`,
        "left": `${dataPx[2][0]}px`,
        "top": `${barHeight + intraPad}px`
    });

    $(".h1 > .head-chart")
        .append($rect0)
        .append($rect1)
        .append($rect2)
        .append($rect3);

    para.gridlines[1].forEach((val) => {
        const $grid1 = $(document.createElement("div"))
        const $grid2 = $(document.createElement("div"))

        $grid1.addClass("grid-line");
        $grid2.addClass("grid-line");

        $grid1.css({
            "left": `${getWidth(val, 2)}px`,
        });
        $grid2.css({
            "left": `${getWidth(val, 2)}px`,
        });

        $(".h1").append($grid1);
        $(".c1").append($grid2);
    });

    for (let i = 1; i < m; ++i) {
        const $row = $(document.createElement("div"))
        const $rect0 = $(document.createElement("div"))
        const $rect1 = $(document.createElement("div"))
        const $rect2 = $(document.createElement("div"))
        const $rect3 = $(document.createElement("div"))

        $rect0.addClass("chart-rect");
        $rect1.addClass("chart-rect");
        $rect2.addClass("chart-rect");
        $rect3.addClass("chart-rect");

        $rect0.attr("data-rect", `2-${i}`);
        $rect1.attr("data-rect", `3-${i}`);
        $rect2.attr("data-rect", `10-${i}`);
        $rect3.attr("data-rect", `11-${i}`);

        $rect0.css({
            "background-color": pal[2],
            "width": `${dataPx[2][i]}px`,
            "height": `${barHeight}px`,
            "left": 0,
            "top": `${barHeight + intraPad}px`
        });
        $rect1.css({
            "background-color": pal[3],
            "width": `${dataPx[3][i]}px`,
            "height": `${barHeight}px`,
            "left": 0,
            "top": 0
        });
        $rect2.css({
            "background-color": pal[10],
            "width": `${dataPx[10][i]}px`,
            "height": `${barHeight}px`,
            "left": `${dataPx[3][i]}px`,
            "top": 0
        });
        $rect3.css({
            "background-color": pal[11],
            "width": `${dataPx[11][i]}px`,
            "height": `${barHeight}px`,
            "left": `${dataPx[2][i]}px`,
            "top": `${barHeight + intraPad}px`
        });

        $row
            .append($rect0)
            .append($rect1)
            .append($rect2)
            .append($rect3);
        $(".c1 > .long-chart").append($row);

        const $text = $(document.createElement("div"))

        $text.addClass("time-axis-label time-axis-label-1");

        const date = getDate(m - 1 - i);

        $text.text(`${date[0].slice(0, 3)} ${date[1]}`);

        $row.append($text);

        $text.css({
            "left": `${-$text.width() - 15}px`,
            "top": `calc(50% - ${$text.height() / 2}px)`
        });
    }
};

const drawChart2 = () => {
    const barHeight = (rowHeight - 2 * intraPad) / 3;

    para.gridlines[2].forEach((val) => {
        const $gridLabel = $(document.createElement("div"))

        $gridLabel.addClass("grid-label");
        $gridLabel.text(formatVal(val, "short"));
        $(".h2").append($gridLabel);

        $gridLabel.css({
            "left": `calc(${getWidth(val, 4)}px - 1px - ${$gridLabel.width() / 2}px)`,
        });
    });

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

    $rect0.attr("data-rect", "4-0");
    $rect1.attr("data-rect", "5-0");
    $rect2.attr("data-rect", "6-0");
    $rect3.attr("data-rect", "7-0");
    $rect4.attr("data-rect", "8-0");
    $rect5.attr("data-rect", "9-0");

    $rect0.css({
        "background-color": pal[4],
        "width": `${dataPx[4][0]}px`,
        "height": `${barHeight}px`,
        "left": 0,
        "top": 0
    });
    $rect1.css({
        "background-color": pal[5],
        "width": `${dataPx[5][0]}px`,
        "height": `${barHeight}px`,
        "left": 0,
        "top": `${barHeight + intraPad}px`
    });
    $rect2.css({
        "background-color": pal[6],
        "width": `${dataPx[6][0]}px`,
        "height": `${barHeight}px`,
        "left": 0,
        "top": `${2 * (barHeight + intraPad)}px`
    });
    $rect3.css({
        "background-color": pal[7],
        "width": `${dataPx[7][0]}px`,
        "height": `${barHeight}px`,
        "left": `${dataPx[4][0]}px`,
        "top": 0
    });
    $rect4.css({
        "background-color": pal[8],
        "width": `${dataPx[8][0]}px`,
        "height": `${barHeight}px`,
        "left": `${dataPx[5][0]}px`,
        "top": `${barHeight + intraPad}px`
    });
    $rect5.css({
        "background-color": pal[9],
        "width": `${dataPx[9][0]}px`,
        "height": `${barHeight}px`,
        "left": `${dataPx[6][0]}px`,
        "top": `${2 * (barHeight + intraPad)}px`
    });

    $(".h2 > .head-chart")
        .append($rect0)
        .append($rect1)
        .append($rect2)
        .append($rect3)
        .append($rect4)
        .append($rect5);

    para.gridlines[2].forEach((val) => {
        const $grid1 = $(document.createElement("div"))
        const $grid2 = $(document.createElement("div"))

        $grid1.addClass("grid-line");
        $grid2.addClass("grid-line");

        $grid1.css({
            "left": `calc(${getWidth(val, 4)}px - 1px)`,
        });
        $grid2.css({
            "left": `calc(${getWidth(val, 4)}px - 1px)`,
        });

        $(".h2").append($grid1);
        $(".c2").append($grid2);
    });

    for (let i = 1; i < m; ++i) {
        const $row = $(document.createElement("div"))
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

        $rect0.attr("data-rect", `4-${i}`);
        $rect1.attr("data-rect", `5-${i}`);
        $rect2.attr("data-rect", `6-${i}`);
        $rect3.attr("data-rect", `7-${i}`);
        $rect4.attr("data-rect", `8-${i}`);
        $rect5.attr("data-rect", `9-${i}`);

        $rect0.css({
            "background-color": pal[4],
            "width": `${dataPx[4][i]}px`,
            "height": `${barHeight}px`,
            "left": 0,
            "top": 0
        });
        $rect1.css({
            "background-color": pal[5],
            "width": `${dataPx[5][i]}px`,
            "height": `${barHeight}px`,
            "left": 0,
            "top": `${barHeight + intraPad}px`
        });
        $rect2.css({
            "background-color": pal[6],
            "width": `${dataPx[6][i]}px`,
            "height": `${barHeight}px`,
            "left": 0,
            "top": `${2 * (barHeight + intraPad)}px`
        });
        $rect3.css({
            "background-color": pal[7],
            "width": `${dataPx[7][i]}px`,
            "height": `${barHeight}px`,
            "left": `${dataPx[4][i]}px`,
            "top": 0
        });
        $rect4.css({
            "background-color": pal[8],
            "width": `${dataPx[8][i]}px`,
            "height": `${barHeight}px`,
            "left": `${dataPx[5][i]}px`,
            "top": `${barHeight + intraPad}px`
        });
        $rect5.css({
            "background-color": pal[9],
            "width": `${dataPx[9][i]}px`,
            "height": `${barHeight}px`,
            "left": `${dataPx[6][i]}px`,
            "top": `${2 * (barHeight + intraPad)}px`
        });

        $row
            .append($rect0)
            .append($rect1)
            .append($rect2)
            .append($rect3)
            .append($rect4)
            .append($rect5);
        $(".c2 > .long-chart").append($row);

        const $text = $(document.createElement("div"))

        $text.addClass("time-axis-label time-axis-label-2");

        const date = getDate(m - 1 - i);

        $text.text(`${date[0].slice(0, 3)} ${date[1]}`);

        $row.append($text);

        $text.css({
            "left": `${-$text.width() - 15}px`,
            "top": `calc(50% - ${$text.height() / 2}px)`
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

            const value = formatVal(data[rect[0]][rect[1]])

            const date = getDate(m - 1 - rect[1]);

            let label1 = `${date[0]} ${date[1]}`;
            let label2 = `${labels[rect[0]]}: ${value}`;

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
    const date = getDate(m - 1);

    $(".title > span").text(`${date[0]} ${date[1]}`);

    updateLegend();
	drawChart0();
	drawChart1();
	drawChart2();
    initTooltip();

    $(window).on("resize", () => {
        showTimeAxis();
    });
    showTimeAxis();
})();

});
