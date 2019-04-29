/**
 * Creates a pseudo-random value generator. The seed must be an integer.
 *
 * Uses an optimized version of the Park-Miller PRNG.
 * http://www.firstpr.com.au/dsp/rand31/
 */
function Random(seed) {
  this._seed = seed % 2147483647;
  if (this._seed <= 0) this._seed += 2147483646;
}

/**
 * Returns a pseudo-random value between 1 and 2^32 - 2.
 */
Random.prototype.next = function() {
  return (this._seed = (this._seed * 16807) % 2147483647);
};

/**
 * Returns a pseudo-random floating point number in range [0, 1).
 */
Random.prototype.nextFloat = function(opt_minOrMax, opt_max) {
  // We know that result of next() will be 1 to 2147483646 (inclusive).
  return (this.next() - 1) / 2147483646;
};

Random.prototype.nextByte = function(opt_minOrMax, opt_max) {
  // We know that result of next() will be 1 to 2147483646 (inclusive).
  return Math.floor((256 * (this.next() - 1)) / 2147483646);
};

function color(context) {
  var index = context.dataIndex;
  let r = new Random(index);
  r.nextByte();
  c =
    "rgba(" + r.nextByte() + ", " + r.nextByte() + ", " + r.nextByte() + ", 1)";
  return c;
}

function setupChart(ctx, gameData) {
  var myLineChart = new Chart(ctx, {
    type: "line",
    data: {
      datasets: Object.keys(gameData.players).map(function(name, index) {
        let history = gameData.players[name];
        let theColor = color({ dataIndex: index });

        return {
          lineTension: 0.2,
          fill: false,
          backgroundColor: theColor,
          borderColor: theColor,
          label: name,
          data: Object.keys(history).map(function(matchNumber) {
            return { x: matchNumber, y: Math.round(history[matchNumber]) };
          })
        };
      })
    },

    options: {
      legend: {
        display: true,
        position: "bottom"
      },
      tooltips: {
        mode: "nearest",
        intersect: false
      },
      scales: {
        xAxes: [
          {
            type: "linear",
            position: "bottom"
          }
        ]
      },
      maintainAspectRatio: false
    }
  });
}
