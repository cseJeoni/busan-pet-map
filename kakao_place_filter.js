// 카카오 검색 API 결과 필터링 기능
// 공원, 산책로 등 산책 가능한 장소만 필터링하는 코드

// 산책 가능한 장소로 고려할 카테고리 목록 정의
const FILTER_CATEGORIES = [
  '도보여행',
  '둘레길',
  '하천',
  '공원',
  '도시근린공원',
  '국립공원',
  '도립공원',
  '산',
  '오름',
  '호수',
  '저수지',
  '수목원,식물원',
];

// 카카오 장소 검색 결과를 산책 가능한 장소만 필터링하는 함수 (일반 필터링)
function filterPlacesByCategory(places) {
  if (!places || !Array.isArray(places)) {
    console.error('유효한 장소 데이터 배열이 아닙니다.');
    return [];
  }
  
  return places.filter((place) => {
    // 장소의 카테고리 정보가 없는 경우
    if (!place.category_name) return false;
    
    // 카테고리 정보를 '>'를 기준으로 분리
    const categories = place.category_name.split(' > ');
    
    // 필터링 카테고리 중 하나라도 포함되어 있으면 true 반환
    return FILTER_CATEGORIES.some((keyword) => categories.includes(keyword));
  });
}

// 카카오 장소 검색 결과를 필터링하는 강화된 필터링
// '여행 > 관광,명소'에 속하면서 산책 가능한 장소만 필터링
function filterPlacesStrict(places) {
  if (!places || !Array.isArray(places)) {
    console.error('유효한 장소 데이터 배열이 아닙니다.');
    return [];
  }
  
  return places.filter((place) => {
    // 장소의 카테고리 정보가 없는 경우
    if (!place.category_name) return false;
    
    // 카테고리 정보를 '>'를 기준으로 분리
    const categories = place.category_name.split(' > ');
    
    // 카테고리가 '여행 > 관광,명소'로 시작하는지 확인
    const isValidPath = categories.length >= 2 && 
                        categories[0] === '여행' && 
                        categories[1] === '관광,명소';
    
    // 관광명소가 아니면 필터링에서 제외
    if (!isValidPath) return false;
    
    // 필터링 카테고리 중 하나라도 포함되어 있으면 true 반환
    return FILTER_CATEGORIES.some((keyword) => categories.includes(keyword));
  });
}

// 공원 관련 필터링 - 특수 케이스 (화장실, 주차장 등 제외)
function filterParkOnly(places) {
  if (!places || !Array.isArray(places)) {
    console.error('유효한 장소 데이터 배열이 아닙니다.');
    return [];
  }
  
  return places.filter((place) => {
    // 장소의 카테고리 정보가 없는 경우
    if (!place.category_name) return false;
    
    // 카테고리 정보를 '>'를 기준으로 분리
    const categories = place.category_name.split(' > ');
    
    // 주요 카테고리가 공원인지 확인
    const isPark = categories.includes('공원');
    
    // 제외할 키워드들 (화장실, 주차장 등이 포함된 공원 관련 시설)
    const excludeKeywords = ['화장실', '주차장', '관리소', '매점', '안내소', '사무소'];
    
    // 제외 키워드가 장소명이나 카테고리에 포함되어 있으면 제외
    const shouldExclude = excludeKeywords.some(keyword => 
      place.place_name.includes(keyword) || 
      categories.some(category => category.includes(keyword))
    );
    
    // 공원이면서 제외 키워드를 포함하지 않는 경우만 true 반환
    return isPark && !shouldExclude;
  });
}

// 카카오 장소 검색 API 호출 후 필터링 예시
function searchAndFilterPlaces(keyword, callback) {
  if (!window.kakao || !window.kakao.maps || !window.kakao.maps.services) {
    console.error('카카오맵 API가 로드되지 않았습니다.');
    return;
  }
  
  // 장소 검색 객체 생성
  const ps = new kakao.maps.services.Places();
  
  // 키워드로 장소 검색
  ps.keywordSearch(keyword, (data, status, pagination) => {
    if (status === kakao.maps.services.Status.OK) {
      // 검색된 장소 중 산책 가능한 장소만 필터링
      const filteredPlaces = filterPlacesByCategory(data);
      
      // 필터링된 결과 콜백으로 전달
      if (callback) callback(filteredPlaces, pagination);
    } else {
      console.error('장소 검색 실패:', status);
      if (callback) callback([], null);
    }
  });
}

// 카카오맵 초기화 및 사용 예시
function initKakaoMap() {
  // 카카오 맵 초기화 코드...
  
  // 공원 검색 및 필터링 예시
  searchAndFilterPlaces('부산 공원', (filteredPlaces) => {
    console.log('필터링된 공원 목록:', filteredPlaces);
    
    // 필터링된 장소를 지도에 마커로 표시하는 로직 추가...
  });
}

// 외부에서 사용할 수 있도록 함수 노출
window.kakaoPlaceFilter = {
  filterPlacesByCategory,
  filterPlacesStrict,
  filterParkOnly,
  searchAndFilterPlaces
};
