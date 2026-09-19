const $ = id => document.getElementById(id);

function val(id) {
    const element = $(id);

    if (!element) {
        return undefined;
    }

    const v = element.value.trim();

    if (v === "") {
        return undefined;
    }

    return isNaN(v) ? v : Number(v);
}


function render(r) {

    const out = $("output");

    const confidenceMap = {
        "High": 90,
        "Medium": 70,
        "Low": 45
    };

    let confidence = r.confidence;

    if (typeof confidence === "string") {
        confidence = confidenceMap[confidence] || 50;
    }

    if (typeof confidence !== "number") {
        confidence = 50;
    }

    const metrics = Array.isArray(r.impacted_metrics)
        ? r.impacted_metrics
        : [];

    const evidence = Array.isArray(r.evidence)
        ? r.evidence
        : [];

    out.innerHTML = `
        <div class="card">
            <div class="rec">
                ${r.recommendation || "No recommendation available."}
            </div>

            <p class="why">
                ${r.why_it_works || ""}
            </p>
        </div>


        <div class="card">
            <b>Impacted metrics</b>

            <div class="metrics" style="margin-top:10px">

                ${
                    metrics.length
                    ? metrics
                        .map(
                            x => `<span class="metric">${x}</span>`
                        )
                        .join("")
                    : "<span>No metrics available</span>"
                }

            </div>
        </div>


        <div class="card">

            <b>Time horizon</b>

            <p class="why">
                ${r.time_horizon || "Not specified"}
            </p>


            <b>Confidence</b>

            <p class="why">
                ${Math.round(confidence)}%
                — based on environmental signals and available evidence.
            </p>

        </div>


        <div class="card">

            <b>Environmental signals</b>

            <div class="signals" style="margin-top:10px">

                ${
                    Array.isArray(r.signals_used) &&
                    r.signals_used.length
                    ? r.signals_used
                        .map(
                            x => `<div class="signal">${x}</div>`
                        )
                        .join("")
                    : "<div>No specific signals detected.</div>"
                }

            </div>

        </div>


        <div class="card">

            <b>Recommended actions</b>

            <ul>

                ${
                    Array.isArray(r.actions) &&
                    r.actions.length
                    ? r.actions
                        .map(
                            x => `<li>${x}</li>`
                        )
                        .join("")
                    : "<li>No additional actions available.</li>"
                }

            </ul>

        </div>


        <div class="card">

            <b>Retrieved evidence</b>

            ${
                evidence.length
                ? evidence
                    .map(e => {

                        const url =
                            e.source_url ||
                            e.url ||
                            "#";

                        const title =
                            e.title ||
                            "Environmental evidence";

                        const organization =
                            e.source_organization ||
                            e.organization ||
                            "Source";

                        const year =
                            e.year ||
                            "";

                        const score =
                            e.retrieval_score ||
                            e.score ||
                            "";

                        return `
                            <a
                                class="source"
                                href="${url}"
                                target="_blank"
                                rel="noopener noreferrer"
                            >

                                <b>${title}</b>

                                <span>
                                    ${organization}
                                    ${year ? " • " + year : ""}
                                    ${score ? " • relevance " + score : ""}
                                </span>

                            </a>
                        `;

                    })
                    .join("")
                : "<p>No matching evidence found.</p>"
            }

        </div>
    `;
}


$("analyze").onclick = async () => {

    $("status").textContent = "Retrieving…";

    $("clarify").classList.add("hidden");


    const body = {

        message: $("message").value,

        soil_organic_carbon:
            val("soc"),

        soil_ph:
            val("ph"),

        soil_moisture:
            val("moist"),

        rainfall:
            val("rain"),

        land_use:
            val("land"),

        pollution_index:
            val("poll")

    };


    console.log(
        "Sending request:",
        body
    );


    try {

        const res = await fetch(
            "/api/analyze",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify(body)
            }
        );


        const d = await res.json();


        console.log(
            "Backend response:",
            d
        );


        if (!res.ok) {

            console.error(
                "API error:",
                d
            );

            $("status").textContent =
                "Error";

            $("output").innerHTML = `
                <div class="empty">

                    <b>Backend validation error</b>

                    <pre>${JSON.stringify(
                        d,
                        null,
                        2
                    )}</pre>

                </div>
            `;

            return;
        }


        if (
            d.status ===
            "needs_clarification"
        ) {

            $("status").textContent =
                "Needs input";


            const questions =
                Array.isArray(d.missing)
                ? d.missing
                : [];


            $("clarify").innerHTML = `
                <b>More information needed:</b>

                <ul>
                    ${
                        questions
                            .map(
                                q =>
                                    `<li>${q}</li>`
                            )
                            .join("")
                    }
                </ul>
            `;


            $("clarify")
                .classList
                .remove("hidden");


            $("output").innerHTML = `
                <div class="empty">

                    Add the requested
                    environmental variables
                    and run the analysis again.

                </div>
            `;


            return;
        }


        if (
            d.status ===
            "complete"
        ) {

            $("status").textContent =
                "Complete";

            render(d);

            return;
        }


        $("status").textContent =
            "Complete";

        render(d);


    } catch (e) {

        console.error(e);


        $("status").textContent =
            "Offline";


        $("output").innerHTML = `
            <div class="empty">

                Start the FastAPI server and
                open:

                <br><br>

                <b>
                    http://127.0.0.1:8000
                </b>

            </div>
        `;
    }
};