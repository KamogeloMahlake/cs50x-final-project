const userDetails = document.getElementById('user-details');
const novel = document.getElementById('novels');
const novelsButton = document.querySelector('.novels-button');
let showNovel = false;

novelsButton.addEventListener("click", async () => {
	if (showNovel === true)
	{
		novel.innerHTML = "";
		showNovel = false;
	}
	else
	{
		let response = await fetch("/profile/novels");
		let novels = await response.json()
		let html = "";

		novels.forEach(novel => {
			html += `<div>
                <p>
					        <a href="/novel/${novel.name}">${novel.name}</a>
				        </p>
                <a href="/profile/${novel.name}/update">
                  <button>Update</button>
                </a>
              </div>`;
		})
		novel.innerHTML += html;
		showNovel = true;
	}
	userDetails.classList.toggle('hidden');
	novel.classList.toggle('hidden');
	novelsButton.textContent = novelsButton.textContent === "All novels" ? "Show Profile" : "All novels";
});

